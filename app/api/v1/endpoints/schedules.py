from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Any, Dict
from datetime import datetime

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.schedule import Schedule
from app.models.teacher import Teacher
from app.models.class_group import ClassGroup
# Importe outros modelos necessários aqui (Subject, Constraint, etc) se for usar

from app.schemas.school_schemas import ScheduleSchema
from app.tasks.generate_schedule import task_generate_schedule
from app.models.subject import Subject
router = APIRouter()


@router.post("/generate", response_model=ScheduleSchema)
async def generate_schedule(
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # 1. Cria o registro de agendamento (status: processing)
    schedule_attempt = Schedule(
        status="processing",
        generated_at=datetime.utcnow(),
        school_id=current_user.school_id
    )

    db.add(schedule_attempt)
    await db.commit()
    await db.refresh(schedule_attempt)

    # 2. Coleta os dados (Serializando para dicionários)

    # --- PROFESSORES ---
    query_teachers = select(Teacher).where(Teacher.school_id == current_user.school_id)
    t_result = await db.execute(query_teachers)
    # Dica: Se precisar das disponibilidades, lembre do selectinload ou carregue aqui
    teachers_data = [{"id": t.id, "name": t.name} for t in t_result.scalars().all()]

    # --- TURMAS ---
    query_classes = select(ClassGroup).where(ClassGroup.school_id == current_user.school_id)
    c_result = await db.execute(query_classes)
    classes_data = [{"id": c.id, "name": c.name, "grade": c.grade} for c in c_result.scalars().all()]
    constraints_data = [{"type": c.type, "data": c.data} for c in const_result.scalars().all()]

    # --- DISCIPLINAS (NOVO) ---
    query_subjects = select(Subject).where(Subject.school_id == current_user.school_id)
    s_result = await db.execute(query_subjects)
    subjects_data = [
        {
            "id": s.id,
            "name": s.name,
            "teacher_id": s.teacher_id,  # Quem dá aula?
            "class_group_id": s.class_group_id,  # Para qual turma?
            "weekly_lessons": s.weekly_lessons,  # Quantas aulas?
            "max_daily_lessons": s.max_daily_lessons,
            "allow_consecutive": s.allow_consecutive
        }
        for s in s_result.scalars().all()
    ]

    # Monta o pacote de dados
    school_data = {
        "teachers": teachers_data,
        "class_groups": classes_data,
        "subjects": subjects_data,
        "constraints": constraints_data
    }

    # 3. Chama a Background Task
    background_tasks.add_task(
        task_generate_schedule,
        schedule_id=schedule_attempt.id,
        school_data=school_data
    )

    return schedule_attempt

@router.get("/{schedule_id}", response_model=ScheduleSchema)
async def read_schedule(
        schedule_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Pega os detalhes de um agendamento específico.
    """
    query = select(Schedule).where(
        Schedule.id == schedule_id,
        Schedule.school_id == current_user.school_id
    )

    result = await db.execute(query)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return schedule


@router.get("/{schedule_id}/grid", response_model=Dict[str, Any])
async def get_schedule_grid(
        schedule_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Retorna a grade formatada visualmente (Turma -> Dias da Semana -> Horários).
    Traduz os IDs para Nomes reais.
    """
    # 1. Busca o Agendamento
    query = select(Schedule).where(
        Schedule.id == schedule_id,
        Schedule.school_id == current_user.school_id
    )
    result = await db.execute(query)
    schedule = result.scalar_one_or_none()

    if not schedule or not schedule.result_data:
        raise HTTPException(status_code=404, detail="Schedule not found or empty")

    # 2. Busca os Nomes (Metadados) para traduzir os IDs
    # Isso evita que o frontend tenha que fazer 50 requisições

    # Professores
    t_res = await db.execute(select(Teacher.id, Teacher.name).where(Teacher.school_id == current_user.school_id))
    teachers_map = {t.id: t.name for t in t_res.all()}

    # Matérias
    s_res = await db.execute(select(Subject.id, Subject.name).where(Subject.school_id == current_user.school_id))
    subjects_map = {s.id: s.name for s in s_res.all()}

    # Turmas
    c_res = await db.execute(
        select(ClassGroup.id, ClassGroup.name).where(ClassGroup.school_id == current_user.school_id))
    classes_map = {c.id: c.name for c in c_res.all()}

    # 3. Monta a Grade
    # Estrutura: { "Nome da Turma": { "Segunda": [Aula1, Aula2...], "Terça": ... } }

    grid = {}
    days_map = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado"}

    # Inicializa a estrutura vazia para todas as turmas que estão na solução
    for item in schedule.result_data:
        c_id = item['class_group_id']
        c_name = classes_map.get(c_id, f"Turma {c_id}")

        if c_name not in grid:
            grid[c_name] = {}
            for d in range(5):  # 0 a 4 (Seg a Sex)
                day_name = days_map[d]
                grid[c_name][day_name] = [None] * 5  # 5 horários vazios

    # Preenche os horários
    for item in schedule.result_data:
        c_id = item['class_group_id']
        t_id = item['teacher_id']
        s_id = item['subject_id']
        day = item['day_of_week']  # 0 a 4
        period = item['period']  # 0 a 4

        c_name = classes_map.get(c_id, f"Turma {c_id}")
        t_name = teachers_map.get(t_id, f"Prof. {t_id}")
        s_name = subjects_map.get(s_id, f"Matéria {s_id}")
        day_name = days_map.get(day, f"Dia {day}")

        # Proteção contra índices fora do limite (caso mude regra de slots)
        if 0 <= period < 5:
            grid[c_name][day_name][period] = {
                "materia": s_name,
                "professor": t_name
            }

    return {
        "schedule_id": schedule_id,
        "status": schedule.status,
        "grid": grid
    }