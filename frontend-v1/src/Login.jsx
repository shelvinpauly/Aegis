import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from "./assets/file.png";
import './css/Login.css';

function Login({ setIsLoggedIn }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    // - Send a POST request to your backend API with username and password
    // - Check the response for success
    // - On success, redirect to the main app using navigate('/path/to/main-app')

    if (username === 'admin' && password === 'password') {
      setIsLoggedIn(true);
      navigate('/app');
    } else {
      alert('Invalid username or password');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-branding">
          <h1 className="login-branding-title">Aegis</h1>
          <img src={logo} alt="Aegis Logo" width="100" height="100"></img>
        </div>
        <form onSubmit={handleSubmit} className="login-form">
          <input
            type="text"
            id="username"
            placeholder='Enter your Username'
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="login-input"
          />
          <input
            type="password"
            id="password"
            placeholder='Enter your Password'
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="login-input"
          />
          <button type="submit" className="login-button">Login</button>
        </form>
      </div>
      <div className="copyright">
        &copy; InterSources Inc 2024
      </div>
    </div>
  );
}

export default Login;