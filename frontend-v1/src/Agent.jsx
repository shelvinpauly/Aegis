import { useState, useEffect } from "react";
import loadingGif from "./assets/spinner.gif";
import lens from "./assets/lens.png";
import logo from "./assets/file.png";
import "./css/Agent.css";

function App() {
    const [prompt, updatePrompt] = useState(undefined);
    const [loading, setLoading] = useState(false);
    const [answer, setAnswer] = useState(undefined);
  
    useEffect(() => {
      if (prompt != null && prompt.trim() === "") {
        setAnswer(undefined);
      }
    }, [prompt]);
  
    const sendPrompt = async (event) => {
      if (event.key !== "Enter") {
        return;
      }
    
      try {
        setLoading(true);
    
        const requestOptions = {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt }),
        };
    
        const res = await fetch("http://127.0.0.1:8080/api/ask", requestOptions);
        console.log('Response status:', res);
    
        if (!res.ok) {
          throw new Error("Something went wrong");
        }
    
        const { message } = await res.json();
        setAnswer(message);
        console.log(message);
      } catch (err) {
        console.error(err, "err");
      } finally {
        setLoading(false);
      }
    };
  
    //need to fetch the user info through an api - comes from the auth blocks
  
    return (
      <div className="app">
          <div className="left-panel">Chat History
            <div className="about">
              About
            </div>
          </div>
          <div className="app-container">          
            <div className="top-bar">
              <h1>Aegis</h1>
              <img src={logo} alt="Aegis Logo" width="50" height="50"></img>
            </div>
            <div className="spotlight__wrapper">
              <input
                type="text"
                className="spotlight__input"
                placeholder="Ask me anything..."
                onChange={(e) => updatePrompt(e.target.value)}
                onKeyDown={(e) => sendPrompt(e)}
                disabled={loading}
                style={{
                  backgroundImage: loading ? `url(${loadingGif})` : `url(${lens})`,
                }}
              />
              <div className="spotlight__answer">
              {answer && <p>{answer}</p>}
              </div>
            </div>
          </div>
      </div>
    );
  }
  
  export default App;