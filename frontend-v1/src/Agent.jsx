import { useState, useEffect, useNavigate } from "react";
import loadingGif from "./assets/spinner.gif";
import lens from "./assets/lens.png";
import logo from "./assets/file.png";
import defaultuser from "./assets/default_profile.png";
import "./css/Agent.css";

function App( {setIsLoggedIn} ) {
    
  const [username, setUsername] = useState('Admin'); 
  const [prompt, updatePrompt] = useState(undefined);
  const [loading, setLoading] = useState(false);
    // const [answer, setAnswer] = useState(undefined);
  
    // useEffect(() => {
    //   if (prompt != null && prompt.trim() === "") {
    //     setAnswer(undefined);
    //   }
    // }, [prompt]);
  
    // const sendPrompt = async (event) => {
    //   if (event.key !== "Enter") {
    //     return;
    //   }
    
    //   try {
    //     setLoading(true);
    
    //     const requestOptions = {
    //       method: "POST",
    //       headers: { "Content-Type": "application/json" },
    //       body: JSON.stringify({ prompt }),
    //     };
    
    //     const res = await fetch("http://127.0.0.1:8080/api/ask", requestOptions);
    //     console.log('Response status:', res);
    
    //     if (!res.ok) {
    //       throw new Error("Something went wrong");
    //     }
    
    //     const { message } = await res.json();
    //     setAnswer(message);
    //     console.log(message);
    //   } catch (err) {
    //     console.error(err, "err");
    //   } finally {
    //     setLoading(false);
    //   }
    // };
  
    //need to fetch the user info through an api - comes from the auth blocks

  // const [isLoggedIn, setIsLoggedIn] = useState(false);
  // const navigate = useNavigate();

  // // Handle redirection and temporary message
  // useEffect(() => {
  //   if (!isLoggedIn) {
  //     // Show temporary message (optional)
  //     const timeoutId = setTimeout(() => {
  //       alert("Logout successful!"); // Replace with desired message display method
  //     }, 20000); // Timeout for 20 seconds

  //     // Redirect after displaying message
  //     setTimeout(() => {
  //       navigate("/login");
  //     }, 22000); // Delay redirect slightly after message timeout

  //     return () => clearTimeout(timeoutId); // Cleanup on component unmount
  //   }
  // }, [isLoggedIn, navigate]);


  const handleLogout = () => {
    if (window.confirm("Are you sure you want to log out?")) {
      // Send a request to the server to invalidate the session (if applicable)
      // localStorage.removeItem('authToken');
  
      setIsLoggedIn(false);
      // Show a temporary message (optional)
      alert("Logout successful!");
    }
  };
  
  
    return (
      <div className="app">
          <div className="left-panel">
          < div className="user-info">
              <img src={defaultuser} width='30' height='30' />
              <span>{username}</span>
            </div>
            <div className="left-panel_console">
              <button>About</button>
              <button>Contact Us</button>
              <button>Guide</button>
              <button onClick={handleLogout}>Logout</button>
            </div>
            
            <div className="left-panel_chat-history">
              Chats
            </div>
          </div>
          <div className="app-container">          
            <div className="top-bar">
              <h1>Aegis</h1>
              {/* <img src={logo} alt="Aegis Logo" width="75" height="75"></img> */}
              <div className="copyright">
                &copy; InterSources Inc 2024
              </div>
            </div>
            <div className="chat-window">
            <img src={logo} alt="Aegis Logo" width="25" height="25"></img>
              <div className="bot-message">
                Hi I am Aegis, your personal AI cybersecurity auditor. Lets start reviewing your IT infrastructure first. Tell me which industry does your company belong to ?
              </div>
              {/* <div className="spotlight__answer">
                {answer && <p>{answer}</p>}
                </div> */}
            </div>
            <div className="input-div">
              <div className="cautionary-message">Aegis may display inaccurate info, so double-check its responses.</div>
              <input type="text" className="spotlight__input" placeholder="Please provide your input/questions here..."
                  onChange={(e) => updatePrompt(e.target.value)} onKeyDown={(e) => sendPrompt(e)}
                  disabled={loading} />
            </div>  
          </div>
      </div>
    );
  }
  
  export default App;