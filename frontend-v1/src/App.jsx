import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Agent from './Agent';
import { useState, useEffect } from "react";

function App() {
  //need to fetch the user info through an api - comes from the auth blocks
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setIsLoggedIn(true);
    }
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
        <Route path="/app" element={isLoggedIn ? <Agent /> : <Navigate to="/login" replace />} />
        <Route path="/" element={isLoggedIn ? <Agent /> : <Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;