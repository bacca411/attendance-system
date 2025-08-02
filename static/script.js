document.addEventListener("DOMContentLoaded", () => {
    const classSelect = document.getElementById("classSelect");
    const studentsContainer = document.getElementById("studentsContainer");
    const studentsTableBody = document.querySelector("#studentsTable tbody");
    const attendanceForm = document.getElementById("attendanceForm");
    const messageDiv = document.getElementById("message");

    // Fetch students on class selection
    classSelect.addEventListener("change", async () => {
        const classId = classSelect.value;
        studentsTableBody.innerHTML = "";
        if (!classId) {
            studentsContainer.classList.add("hidden");
            return;
        }

        const response = await fetch(`/students/${classId}`);
        const students = await response.json();

        students.forEach(student => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${student.name}</td>
                <td><input type="radio" name="student_${student.id}" value="Present" required></td>
                <td><input type="radio" name="student_${student.id}" value="Absent"></td>
            `;
            studentsTableBody.appendChild(row);
        });

        studentsContainer.classList.remove("hidden");
    });

    // Submit attendance
    attendanceForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(attendanceForm);
        const attendance = [];

        for (let [key, value] of formData.entries()) {
            const studentId = key.split("_")[1];
            attendance.push({ student_id: studentId, status: value });
        }

        const response = await fetch("/attendance", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ attendance })
        });

        const result = await response.json();
        messageDiv.textContent = result.message;
        messageDiv.classList.remove("hidden");
        attendanceForm.reset();
        studentsContainer.classList.add("hidden");
    });
});
