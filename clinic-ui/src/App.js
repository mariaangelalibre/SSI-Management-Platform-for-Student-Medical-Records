import React, { useState } from 'react';
import Login from './components/Login';
import StudentList from './components/StudentList';
import CredentialRequest from './components/CredentialRequest';
import './styles/App.css';

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [selectedStudent, setSelectedStudent] = useState(null);

    const handleLogin = (loggedIn) => {
        setIsLoggedIn(loggedIn);
    };

    return (
        <div className="App">
            <header className="App-header">CEA Curekey</header>
            {isLoggedIn ? (
                <div>
                    <StudentList onSelectStudent={setSelectedStudent} />
                    {selectedStudent && (
                        <CredentialRequest student={selectedStudent} />
                    )}
                </div>
            ) : (
                <Login onLogin={handleLogin} />
            )}
        </div>
    );
}

export default App;
