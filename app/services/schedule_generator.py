from ortools.sat.python import cp_model
from typing import Dict, Any, List


class ScheduleGeneratorService:
    def __init__(self, school_data: Dict[str, Any]):
        self.data = school_data
        self.teachers = school_data.get("teachers", [])
        self.groups = school_data.get("class_groups", [])
        self.subjects = school_data.get("subjects", [])

        self.model = cp_model.CpModel()
        self.vars = {}  # Dicionário para guardar as variáveis de decisão

        # Configurações básicas (podem vir do banco no futuro)
        self.days = 5  # 0=Seg, 1=Ter, 2=Qua, 3=Qui, 4=Sex
        self.slots = 5  # 5 aulas por dia

    def solve(self) -> Dict[str, Any]:
        print(f"--> [Algoritmo] Iniciando com {len(self.subjects)} disciplinas...")

        # 1. CRIAR VARIÁVEIS
        # Variável x[turma, professor, materia, dia, horario] -> 1 se tiver aula, 0 se não
        for s in self.subjects:
            g_id = s['class_group_id']
            t_id = s['teacher_id']
            s_id = s['id']

            # Se faltar dados vitais, pula
            if not g_id or not t_id:
                continue

            for d in range(self.days):
                for h in range(self.slots):
                    # Cria a variável booleana para este slot
                    self.vars[(g_id, t_id, s_id, d, h)] = self.model.NewBoolVar(
                        f"x_g{g_id}_t{t_id}_s{s_id}_d{d}_h{h}"
                    )

        # 2. RESTRIÇÃO: Carga Horária (A MAIS IMPORTANTE)
        # "A soma das aulas de Matemática tem que ser igual a 4"
        for s in self.subjects:
            s_id = s['id']
            g_id = s['class_group_id']
            t_id = s['teacher_id']
            required_lessons = s.get('weekly_lessons', 0)

            if required_lessons > 0:
                # Coleta todas as variáveis dessa matéria específica
                materia_vars = []
                for d in range(self.days):
                    for h in range(self.slots):
                        if (g_id, t_id, s_id, d, h) in self.vars:
                            materia_vars.append(self.vars[(g_id, t_id, s_id, d, h)])

                if materia_vars:
                    # Adiciona a regra: Soma tem que ser EXATAMENTE igual ao exigido
                    self.model.Add(sum(materia_vars) == required_lessons)

        # 3. RESTRIÇÃO: Choque de Horário (Turma)
        # Uma turma não pode ter 2 aulas no mesmo horário
        for g in self.groups:
            g_id = g['id']
            for d in range(self.days):
                for h in range(self.slots):
                    # Pega todas as aulas dessa turma nesse horário (de qualquer matéria)
                    vars_in_slot = [
                        self.vars[key] for key in self.vars
                        if key[0] == g_id and key[3] == d and key[4] == h
                    ]
                    if vars_in_slot:
                        self.model.Add(sum(vars_in_slot) <= 1)

        # 4. RESTRIÇÃO: Choque de Horário (Professor)
        # Um professor não pode dar 2 aulas no mesmo horário (em turmas diferentes)
        for t in self.teachers:
            t_id = t['id']
            for d in range(self.days):
                for h in range(self.slots):
                    # Pega todas as aulas desse professor nesse horário
                    vars_in_slot = [
                        self.vars[key] for key in self.vars
                        if key[1] == t_id and key[3] == d and key[4] == h
                    ]
                    if vars_in_slot:
                        self.model.Add(sum(vars_in_slot) <= 1)

        # 5. RESTRIÇÃO: Máximo de Aulas Diárias (Opcional - evita dobradinha tripla)
        for s in self.subjects:
            max_daily = s.get('max_daily_lessons', 2)  # Padrão: max 2 aulas por dia
            g_id = s['class_group_id']
            t_id = s['teacher_id']
            s_id = s['id']

            for d in range(self.days):
                daily_vars = []
                for h in range(self.slots):
                    if (g_id, t_id, s_id, d, h) in self.vars:
                        daily_vars.append(self.vars[(g_id, t_id, s_id, d, h)])

                if daily_vars:
                    self.model.Add(sum(daily_vars) <= max_daily)

        for c in self.data.get("constraints", []):
            if c['type'] == 'TEACHER_UNAVAILABILITY':
                t_id = c['data'].get('teacher_id')
                blocked_day = c['data'].get('day_of_week')  # 0=Seg, 4=Sex

                print(f"--> [Regra] Bloqueando Prof {t_id} no dia {blocked_day}")

                if t_id is not None and blocked_day is not None:
                    # Varre todos os horários desse dia
                    for h in range(self.slots):
                        # Encontra todas as variáveis de aula deste professor neste dia/horário
                        vars_to_block = []
                        for key, var in self.vars.items():
                            # key = (g_id, teacher_id, s_id, day, period)
                            if key[1] == t_id and key[3] == blocked_day and key[4] == h:
                                vars_to_block.append(var)

                        # Se encontrou aulas possíveis, força a soma ser 0 (Nenhuma aula permitida)
                        if vars_to_block:
                            self.model.Add(sum(vars_to_block) == 0)

            # --- EXECUTAR O SOLVER ---
        solver = cp_model.CpSolver()

        # Tempo limite para não travar o servidor (30 segundos)
        solver.parameters.max_time_in_seconds = 30.0

        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"--> [Algoritmo] Solução encontrada! (Status: {status})")
            return {
                "status": "success",
                "result": self._format_solution(solver)
            }
        else:
            print(f"--> [Algoritmo] Nenhuma solução possível. Verifique as restrições.")
            return {
                "status": "error",
                "error": "Impossível gerar grade. Conflito de restrições ou falta de tempo."
            }

    def _format_solution(self, solver):
        """Converte as variáveis do OR-Tools para JSON legível"""
        schedule_json = []

        # Mapeamento para nomes legíveis (opcional, ajuda no debug)
        days_map = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex"}

        for (g_id, t_id, s_id, d, h), variable in self.vars.items():
            if solver.Value(variable) == 1:
                # Encontrou uma aula marcada!
                schedule_json.append({
                    "class_group_id": g_id,
                    "teacher_id": t_id,
                    "subject_id": s_id,
                    "day_of_week": d,  # 0 a 4
                    "day_name": days_map.get(d),
                    "period": h,  # 0 a 4 (Horário da aula)
                    "period_index": h + 1  # 1º horário, 2º horário...
                })

        return schedule_json