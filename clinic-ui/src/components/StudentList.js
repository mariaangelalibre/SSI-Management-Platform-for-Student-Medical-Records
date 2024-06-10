import React from 'react';
import '../styles/StudentList.css';

const StudentList = ({ onSelectStudent }) => {
    const students = [
        { id: 1, name: 'Jade Aubrey Abiog' },
        { id: 2, name: 'Patricia Andy Aquino' },
        { id: 3, name: 'Maria Angela Libre' },
    ];

    return (
        <div className="student-list">
            <h2 className="small-student">Student List</h2>
            <ul>
                {students.map(student => (
                    <li key={student.id} onClick={() => onSelectStudent(student)}>
                        {student.name}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default StudentList;
