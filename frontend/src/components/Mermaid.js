import React, { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

const Mermaid = ({ chart }) => {
  const containerRef = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: "default",
      securityLevel: "loose",
      logLevel: 5, // Suppress logs
    });

    const renderChart = async () => {
      if (!chart || !containerRef.current) return;

      try {
        setError(null);
        // Clear previous content
        containerRef.current.innerHTML = "";
        
        // Generate a unique ID for this render to prevent conflicts
        const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
        
        // Mermaid v10+ rendering
        const { svg } = await mermaid.render(id, chart);
        
        if (containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      } catch (err) {
        console.error("Mermaid Render Error:", err);
        setError("Invalid Mindmap Syntax");
      }
    };

    renderChart();
  }, [chart]);

  if (error) {
    return (
      <div style={{ color: "red", padding: "10px", border: "1px solid red", fontSize: "12px" }}>
        <strong>Mindmap Error:</strong> The AI generated invalid syntax.<br/>
        <pre style={{ marginTop: "5px", whiteSpace: "pre-wrap" }}>{chart}</pre>
      </div>
    );
  }

  return (
    <div 
      className="mermaid-container" 
      ref={containerRef} 
      style={{ width: "100%", overflowX: "auto", minHeight: "100px", textAlign: "center" }} 
    />
  );
};

export default Mermaid;