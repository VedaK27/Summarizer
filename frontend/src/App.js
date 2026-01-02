import { useEffect, useState } from "react";
import SplashScreen from "./components/SplashScreen";
import IntroScreen from "./components/IntroScreen";
import Home from "./components/Home";
import "./App.css";

function App() {
  const [screen, setScreen] = useState("splash");

  useEffect(() => {
    if (screen === "splash") {
      setTimeout(() => setScreen("intro"), 2500);
    }

    if (screen === "intro") {
      setTimeout(() => setScreen("home"), 5000);
    }
  }, [screen]);

  if (screen === "splash") return <SplashScreen />;
  if (screen === "intro") return <IntroScreen />;
  return <Home />;
}

export default App;
