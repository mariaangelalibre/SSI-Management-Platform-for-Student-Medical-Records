import React, { useState } from 'react';
import '../styles/Login.css';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    if (username === 'hyperledgerandy' && password === '123') {
      onLogin(true);
    } else {
      setLoginError('Incorrect username or password');
    }
  };

  return (
    <div className="App login-background">
      <header className="App-header">CEA Curekey</header>
      <div className="wrapper-login">
        <div className="title-login">Login Form</div>
        <form onSubmit={handleLogin}>
          <div className="field">
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <label>Username</label>
          </div>
          <div className="field">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <label>Password</label>
          </div>
          <div className="field">
            <input type="submit" value="Login" />
          </div>
          {loginError && <div className="error-message">{loginError}</div>}
        </form>
      </div>
    </div>
  );
};

export default Login;
