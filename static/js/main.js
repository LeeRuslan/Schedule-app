document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('schedule-grid')) {
        loadSchedule();
        loadTeachersPanel();
        loadGroupsFilter();
        setupTopButtons();
        setupGroupSearch();     
        setupTeacherSearch();   
    }
});

// ================== РАСПИСАНИЕ ==================
async function loadSchedule() {
    try {
        const [lessonsRes, groupsRes] = await Promise.all([
            fetch('/api/lessons'), fetch('/api/groups')
        ]);
        const lessons = await lessonsRes.json();
        const groups = await groupsRes.json();
        renderScheduleTable(groups, lessons);
    } catch (e) {
        console.error('Ошибка загрузки:', e);
    }
}

function renderScheduleTable(groups, lessons) {
    const grid = document.getElementById('schedule-grid');
    if (!grid) return;

    if (groups.length === 0) {
        grid.innerHTML = '<div class="empty-state">Нет учебных групп. Добавьте группы в разделе «Группы».</div>';
        return;
    }

    const days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'];
    const pairs = [1, 2, 3, 4];
    const times = { 1: '08:30 – 10:10', 2: '10:30 – 12:10', 3: '12:30 – 14:10', 4: '14:30 – 16:10' };

    let html = '<table class="schedule-table"><thead><tr><th>День / Пара</th>';
    groups.forEach(g => {
        html += `<th>${g.name}<small>${g.speciality || ''} ${g.course ? g.course + ' курс' : ''}</small></th>`;
    });
    html += '</tr></thead><tbody>';

    days.forEach(day => {
        html += `<tr class="day-header-row"><td colspan="${groups.length + 1}">${day.toUpperCase()}</td></tr>`;
        pairs.forEach(pair => {
            html += `<tr><td class="time-cell">${pair} пара<small>${times[pair]}</small></td>`;
            groups.forEach(group => {
                const cellLessons = lessons.filter(l =>
                    l.group_id === group.id && l.day === day &&
                    (l.week1_lesson === pair || l.week2_lesson === pair)
                );
                html += `<td class="schedule-cell" data-group="${group.id}" data-day="${day}" data-pair="${pair}">`;
                cellLessons.forEach(lesson => { html += renderLessonCard(lesson); });
                html += '</td>';
            });
            html += '</tr>';
        });
    });
    html += '</tbody></table>';
    grid.innerHTML = html;

    // Обработчики
    document.querySelectorAll('.lesson-card').forEach(card => {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
        card.addEventListener('click', () => openEditModal(card.dataset.id));
    });
    document.querySelectorAll('.schedule-cell').forEach(cell => {
        cell.addEventListener('dragover', e => { e.preventDefault(); cell.classList.add('drag-over'); });
        cell.addEventListener('dragleave', () => cell.classList.remove('drag-over'));
        cell.addEventListener('drop', e => { cell.classList.remove('drag-over'); handleDrop(e); });
    });
}

function renderLessonCard(lesson) {
    const w1 = lesson.week1_lesson > 0 ? `${lesson.week1_lesson} пара` : '—';
    const w2 = lesson.week2_lesson > 0 ? `${lesson.week2_lesson} пара` : '—';
    return `
        <div class="lesson-card" draggable="true" data-id="${lesson.id}" style="border-left-color: ${lesson.teacher_color}">
            <div class="teacher-short">${lesson.teacher_short || lesson.teacher_name}</div>
            <div class="subject-name">${lesson.subject_name}</div>
            <div class="weeks-info">1 нед: ${w1}<br>2 нед: ${w2}</div>
            <div class="room">каб. ${lesson.classroom_name || '—'}</div>
        </div>`;
}

// ================== ПАНЕЛЬ ПРЕПОДАВАТЕЛЕЙ ==================
async function loadTeachersPanel() {
    const container = document.getElementById('teachers-list');
    if (!container) return;
    const res = await fetch('/api/teachers');
    const teachers = await res.json();
    container.innerHTML = '';
    teachers.forEach(t => {
        const div = document.createElement('div');
        div.className = 'teacher-item';
        div.dataset.teacherId = t.id;
        div.innerHTML = `
            <div class="teacher-color" style="background:${t.color}"></div>
            <div class="teacher-info">
                <div class="teacher-short-name">${t.short_name || t.name}</div>
                <div class="teacher-subjects-preview">${t.subjects.map(s => s.name).join(', ')}</div>
            </div>`;
        div.addEventListener('click', () => toggleSubjects(t, div));
        container.appendChild(div);
    });
}

async function toggleSubjects(teacher, element) {
    const next = element.nextElementSibling;
    if (next && next.classList.contains('subjects-list')) {
        next.remove();
        element.classList.remove('expanded');
        return;
    }
    document.querySelectorAll('.subjects-list').forEach(el => el.remove());
    document.querySelectorAll('.teacher-item.expanded').forEach(el => el.classList.remove('expanded'));

    element.classList.add('expanded');
    const res = await fetch(`/api/teachers/${teacher.id}/subjects`);
    const subjects = await res.json();
    const list = document.createElement('div');
    list.className = 'subjects-list';
    subjects.forEach(s => {
        const item = document.createElement('div');
        item.className = 'subject-item';
        item.textContent = s.name;
        item.draggable = true;
        item.dataset.teacherId = teacher.id;
        item.dataset.subjectId = s.id;
        item.dataset.teacherShort = teacher.short_name || teacher.name;
        item.dataset.teacherColor = teacher.color;
        item.dataset.teacherName = teacher.name;
        item.dataset.subjectName = s.name;
        item.addEventListener('dragstart', handleDragStartFromPanel);
        item.addEventListener('dragend', handleDragEnd);
        list.appendChild(item);
    });
    element.after(list);
}

function loadGroupsFilter() {
    const select = document.getElementById('group-filter');
    if (!select) return;
    fetch('/api/groups').then(r => r.json()).then(groups => {
        groups.forEach(g => {
            const opt = document.createElement('option');
            opt.value = g.id;
            opt.textContent = g.name;
            select.appendChild(opt);
        });
    });
}

// ================== ВЕРХНИЕ КНОПКИ ==================
function setupTopButtons() {
    document.getElementById('btn-new')?.addEventListener('click', () => {
        if (confirm('Создать новый план? Текущее расписание будет очищено.')) clearAllSchedule();
    });
    document.getElementById('btn-save')?.addEventListener('click', () => {
        alert('Расписание сохраняется автоматически в базе данных SQLite.');
    });
    document.getElementById('btn-clear')?.addEventListener('click', () => {
        if (confirm('Удалить ВСЕ занятия из расписания?')) clearAllSchedule();
    });
    document.getElementById('btn-print')?.addEventListener('click', () => window.print());
    document.getElementById('btn-settings')?.addEventListener('click', () => window.location.href = '/settings');
}

async function clearAllSchedule() {
    if (!confirm('Удалить все занятия?')) return;
    await fetch('/api/lessons/clear', { method: 'POST' });
    loadSchedule();
}

function deleteSelectedLesson() {
    alert('Кликните на карточку занятия, чтобы открыть форму редактирования и удалить.');
}

function copyDay() {
    alert('Функция копирования дня — расширение. Реализуйте по аналогии с API.');
}

// ================== МОДАЛЬНОЕ ОКНО РЕДАКТИРОВАНИЯ ==================
async function openEditModal(lessonId) {
    const res = await fetch(`/api/lessons/${lessonId}`);
    if (!res.ok) return;
    const l = await res.json();

    const [groups, teachers, subjects, classrooms] = await Promise.all([
        fetch('/api/groups').then(r => r.json()),
        fetch('/api/teachers').then(r => r.json()),
        fetch('/api/subjects').then(r => r.json()),
        fetch('/api/classrooms').then(r => r.json()),
    ]);

    const days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'];
    const pairsOptions = (sel) => [0, 1, 2, 3, 4].map(p =>
        `<option value="${p}" ${p === sel ? 'selected' : ''}>${p === 0 ? '—' : p + ' пара'}</option>`).join('');

    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal">
            <h3>Редактирование занятия</h3>
            <div class="modal-field"><label>Группа</label>
                <select id="edit-group">${groups.map(g => `<option value="${g.id}" ${g.id === l.group_id ? 'selected' : ''}>${g.name}</option>`).join('')}</select>
            </div>
            <div class="modal-field"><label>Преподаватель</label>
                <select id="edit-teacher">${teachers.map(t => `<option value="${t.id}" ${t.id === l.teacher_id ? 'selected' : ''}>${t.name}</option>`).join('')}</select>
            </div>
            <div class="modal-field"><label>Дисциплина</label>
                <select id="edit-subject">${subjects.map(s => `<option value="${s.id}" ${s.id === l.subject_id ? 'selected' : ''}>${s.name}</option>`).join('')}</select>
            </div>
            <div class="modal-field"><label>День</label>
                <select id="edit-day">${days.map(d => `<option ${d === l.day ? 'selected' : ''}>${d}</option>`).join('')}</select>
            </div>
            <div class="modal-field"><label>1 неделя</label>
                <select id="edit-w1">${pairsOptions(l.week1_lesson)}</select>
            </div>
            <div class="modal-field"><label>2 неделя</label>
                <select id="edit-w2">${pairsOptions(l.week2_lesson)}</select>
            </div>
            <div class="modal-field"><label>Кабинет</label>
                <select id="edit-classroom">
                    <option value="">—</option>
                    ${classrooms.map(c => `<option value="${c.id}" ${c.id === l.classroom_id ? 'selected' : ''}>${c.name}</option>`).join('')}
                </select>
            </div>
            <div class="modal-actions">
                <button class="btn" id="edit-delete" style="color:#dc2626">Удалить</button>
                <button class="btn" id="edit-cancel">Отмена</button>
                <button class="btn btn-primary" id="edit-save">Сохранить</button>
            </div>
        </div>`;
    document.body.appendChild(modal);

    modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });

    document.getElementById('edit-cancel').onclick = () => modal.remove();
    document.getElementById('edit-delete').onclick = async () => {
        if (!confirm('Удалить занятие?')) return;
        await fetch(`/api/lessons/${lessonId}`, { method: 'DELETE' });
        modal.remove();
        loadSchedule();
    };
    document.getElementById('edit-save').onclick = async () => {
        const data = {
            group_id: parseInt(document.getElementById('edit-group').value),
            teacher_id: parseInt(document.getElementById('edit-teacher').value),
            subject_id: parseInt(document.getElementById('edit-subject').value),
            day: document.getElementById('edit-day').value,
            week1_lesson: parseInt(document.getElementById('edit-w1').value),
            week2_lesson: parseInt(document.getElementById('edit-w2').value),
            classroom_id: document.getElementById('edit-classroom').value ? parseInt(document.getElementById('edit-classroom').value) : null,
        };
        const r = await fetch(`/api/lessons/${lessonId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (r.ok) {
            modal.remove();
            loadSchedule();
        } else {
            const err = await r.json();
            alert(err.error || 'Ошибка');
        }
    };
}
// ================== ПОИСК ПО ГРУППАМ ==================
function setupGroupSearch() {
    const input = document.getElementById('search-groups');
    if (!input) return;

    input.addEventListener('input', () => {
        const query = input.value.trim().toLowerCase();

        // Скрываем/показываем столбцы групп
        const headers = document.querySelectorAll('.schedule-table thead th');
        const cellsByColumn = {};   // индекс колонки -> массив ячеек

        // Заголовки (кроме первого — «День / Пара»)
        headers.forEach((th, idx) => {
            if (idx === 0) return;
            const text = th.textContent.toLowerCase();
            const match = !query || text.includes(query);
            th.style.display = match ? '' : 'none';
            cellsByColumn[idx] = { match };
        });

        // Ячейки в строках
        document.querySelectorAll('.schedule-table tbody tr').forEach(tr => {
            const cells = tr.querySelectorAll('td');
            cells.forEach((td, idx) => {
                // idx=0 — либо заголовок дня (colspan), либо time-cell
                if (td.classList.contains('day-header')) return; // не трогаем
                if (idx === 0) return; // колонка «время»

                const colIdx = idx; // совпадает с индексом th
                if (cellsByColumn[colIdx]) {
                    td.style.display = cellsByColumn[colIdx].match ? '' : 'none';
                }
            });
        });

        // Если ничего не найдено — показать уведомление
        const visibleGroups = [...headers].slice(1).filter(th => th.style.display !== 'none');
        const existing = document.getElementById('no-groups-msg');
        if (visibleGroups.length === 0 && query) {
            if (!existing) {
                const msg = document.createElement('div');
                msg.id = 'no-groups-msg';
                msg.className = 'empty-state';
                msg.textContent = 'Группы не найдены по запросу: «' + query + '»';
                document.getElementById('schedule-grid').prepend(msg);
            }
        } else if (existing) {
            existing.remove();
        }
    });

    // Сброс при очистке
    input.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            input.value = '';
            input.dispatchEvent(new Event('input'));
        }
    });
}

// ================== ПОИСК ПО ПРЕПОДАВАТЕЛЯМ (панель справа) ==================
function setupTeacherSearch() {
    const input = document.getElementById('teacher-search');
    if (!input) return;

    input.addEventListener('input', () => {
        const query = input.value.trim().toLowerCase();

        document.querySelectorAll('#teachers-list .teacher-item').forEach(item => {
            const name = item.querySelector('.teacher-short-name')?.textContent.toLowerCase() || '';
            const preview = item.querySelector('.teacher-subjects-preview')?.textContent.toLowerCase() || '';
            const match = !query || name.includes(query) || preview.includes(query);
            item.style.display = match ? '' : 'none';

            // Скрываем привязанный список дисциплин, если родитель скрыт
            const next = item.nextElementSibling;
            if (next && next.classList.contains('subjects-list') && !match) {
                next.style.display = 'none';
            } else if (next && next.classList.contains('subjects-list') && match) {
                next.style.display = '';
            }
        });

        // Если ничего не найдено
        const visible = [...document.querySelectorAll('#teachers-list .teacher-item')]
            .filter(el => el.style.display !== 'none');
        const container = document.getElementById('teachers-list');
        let msg = container.querySelector('.no-teachers-msg');
        if (visible.length === 0 && query) {
            if (!msg) {
                msg = document.createElement('div');
                msg.className = 'no-teachers-msg';
                msg.style.cssText = 'padding: 20px; text-align: center; color: #94a3b8; font-size: 11px;';
                msg.textContent = 'Преподаватели не найдены';
                container.appendChild(msg);
            }
        } else if (msg) {
            msg.remove();
        }
    });

    input.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            input.value = '';
            input.dispatchEvent(new Event('input'));
        }
    });
}