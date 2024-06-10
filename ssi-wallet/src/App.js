import React, { useState } from 'react';
import Login from './components/Login';
import NavBar from './components/NavBar';
import Credentials from './components/Credentials';
import Requests from './components/Requests';

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [activePage, setActivePage] = useState('credentials');
    const [authorizedInfo, setAuthorizedInfo] = useState([]);

    const handleLogin = (loggedIn) => {
      setIsLoggedIn(loggedIn);
    };

    const handleAuthorize = (info) => {
        setAuthorizedInfo([...authorizedInfo, info]);
    };

    const handleDeny = () => {
        setAuthorizedInfo([]);
    };

    return (
        <div className="App">
            {isLoggedIn ? (
                <div>
                    <NavBar setActivePage={setActivePage} />
                    {activePage === 'credentials' && <Credentials />}
                    {activePage === 'requests' && (
                        <Requests
                            authorizedInfo={authorizedInfo}
                            handleAuthorize={handleAuthorize}
                            handleDeny={handleDeny}
                        />
                    )}
                </div>
            ) : (
                <Login onLogin={handleLogin} />
            )}
        </div>
    );
}

export default App;
