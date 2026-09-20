let draggedItem = null;
let draggedFromPanel = false;

function handleDragStart(e) {
    draggedItem = e.target.closest('.lesson-card');
    draggedFromPanel = false;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', draggedItem.dataset.id);
    draggedItem.classList.add('dragging');
}

function handleDragStartFromPanel(e) {
    draggedItem = e.target;
    draggedFromPanel = true;
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('text/plain', JSON.stringify({
        teacherId: draggedItem.dataset.teacherId,
        subjectId: draggedItem.dataset.subjectId,
        teacherShort: draggedItem.dataset.teacherShort,
        teacherColor: draggedItem.dataset.teacherColor,
        teacherName: draggedItem.dataset.teacherName,
        subjectName: draggedItem.dataset.subjectName,
    }));
    e.target.style.opacity = '0.5';
}

function handleDragEnd() {
    if (draggedItem) {
        draggedItem.style.opacity = '1';
        draggedItem.classList.remove('dragging');
    }
    draggedItem = null;
    draggedFromPanel = false;
}

async function handleDrop(e) {
    e.preventDefault();
    const cell = e.target.closest('.schedule-cell');
    if (!cell) return;

    const groupId = parseInt(cell.dataset.group);
    const day = cell.dataset.day;
    const pair = parseInt(cell.dataset.pair);

    if (draggedFromPanel) {
        const data = JSON.parse(e.dataTransfer.getData('text/plain'));
        const res = await fetch('/api/lessons', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                group_id: groupId,
                teacher_id: parseInt(data.teacherId),
                subject_id: parseInt(data.subjectId),
                day: day,
                week1_lesson: pair,
                week2_lesson: pair,
                classroom_id: null,
                lesson_type: 'Лекция'
            })
        });
        if (res.ok) {
            loadSchedule();
        } else {
            const err = await res.json();
            alert('⚠️ ' + (err.error || 'Ошибка при создании'));
        }
    } else if (draggedItem) {
        const lessonId = draggedItem.dataset.id;
        const current = await fetch(`/api/lessons/${lessonId}`).then(r => r.json());
        const res = await fetch(`/api/lessons/${lessonId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                group_id: groupId,
                day: day,
                week1_lesson: pair,
                week2_lesson: current.week2_lesson === current.week1_lesson ? pair : current.week2_lesson
            })
        });
        if (res.ok) {
            loadSchedule();
        } else {
            const err = await res.json();
            alert('⚠️ ' + (err.error || 'Ошибка при перемещении'));
        }
    }
}