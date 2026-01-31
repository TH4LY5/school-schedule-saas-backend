import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.schedule import Schedule
from app.services.schedule_generator import ScheduleGeneratorService


async def task_generate_schedule(schedule_id: int, school_data: dict, db_session=None):
    """
    Função Worker que roda em background.
    Adaptada para não travar a API (usando thread) e salvar via AsyncSession.

    :param db_session: Ignorado (mantido apenas para compatibilidade se passado por engano),
                       pois criamos nossa própria sessão aqui.
    """
    print(
        f"--> [Task] Iniciando geração da grade {schedule_id} com {len(school_data.get('teachers', []))} professores.")

    # ---------------------------------------------------------
    # 1. EXECUÇÃO DO ALGORITMO (CPU BOUND)
    # ---------------------------------------------------------
    try:
        # Instancia o serviço
        service = ScheduleGeneratorService(school_data)

        # MÁGICA AQUI: O 'to_thread' joga o processamento pesado (solve) 
        # para uma thread separada, liberando o FastAPI para receber outras requisições.
        result = await asyncio.to_thread(service.solve)

        # Define status final baseado no retorno do service
        final_status = "completed" if result.get("status") == "success" else "error"
        final_data = result.get("result") if final_status == "completed" else result

        print(f"--> [Task] Algoritmo finalizado. Status: {final_status}")

    except Exception as e:
        print(f"--> [Task] Erro fatal no algoritmo: {str(e)}")
        final_status = "error"
        final_data = {"error": str(e)}

    # ---------------------------------------------------------
    # 2. ATUALIZAÇÃO DO BANCO DE DADOS (IO BOUND)
    # ---------------------------------------------------------
    # Como a sessão original fechou quando a requisição HTTP acabou,
    # abrimos uma nova conexão exclusiva para esta task.
    async with AsyncSessionLocal() as session:
        try:
            # Busca o agendamento pelo ID
            query = select(Schedule).where(Schedule.id == schedule_id)
            db_result = await session.execute(query)
            schedule = db_result.scalar_one_or_none()

            if schedule:
                # Atualiza os campos
                schedule.status = final_status
                schedule.result_data = final_data  # Certifique-se de ter criado esta coluna JSON no banco

                # Salva as alterações
                await session.commit()
                print(f"--> [Task] Banco de dados atualizado com sucesso (ID: {schedule_id}).")
            else:
                print(f"--> [Task] Erro Crítico: Schedule {schedule_id} não encontrado no banco para atualização.")

        except Exception as e:
            print(f"--> [Task] Erro ao salvar no banco: {str(e)}")
            await session.rollback()