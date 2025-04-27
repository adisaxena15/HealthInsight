import React, { useState } from "react";
import { Navbar } from "../components/ui/navbar";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import SymptomWordCloud from "../components/ui/SymptomWordCloud";

export default function SymptomGraph() {
  const [keyword, setKeyword] = useState("");
  const [showMessage, setShowMessage] = useState(false);
  //const [graphData, setGraphData] = useState([]);
  const [formattedWords, setFormattedWords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasResults, setHasResults] = useState(true);

  const handleSearch = async () => {
    if (!keyword.trim()) {
      setError("Please enter a keyword to search");
      setHasResults(false);
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/symptomGraph', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keyword: keyword }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (!data.results || !Array.isArray(data.results)) {
        throw new Error('Invalid data format received from backend');
      }
      
      if (data.results.length === 0) {
        setHasResults(false);
        setFormattedWords([]);
      } else {
        setHasResults(true);
        const formattedWords = data.results.map(item => {
          const specialty = item.specialty || 'Unknown Specialty';
          const count = item.count || 0;
          return [specialty.trim().toUpperCase(), count];
        });
        
        setFormattedWords(formattedWords);
      }
      
      setShowMessage(true);
    } catch (error) {
      console.error("Error fetching data:", error.message || error);
      setError(error.message || 'An error occurred while fetching data');
      setHasResults(false);
    } finally {
      setLoading(false);
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <main className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto py-16">
        <h1 className="text-4xl font-bold mb-8 text-center text-primary">
          Symptom-Diagnosis Graph Visualization
        </h1>
        <p className="text-xl mb-8 max-w-3xl mx-auto text-justify">
          This interactive graph visualizes the relationships between symptoms and diagnoses. Explore connections,
          identify patterns, and gain insights into how different health conditions are interrelated.
        </p>

        <div className="max-w-xl mx-auto flex gap-4 mb-8">
          <Input
            type="text"
            placeholder="Enter keyword (e.g., fever)"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <Button onClick={handleSearch} disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </Button>
        </div>

        {error && (
          <div className="text-center text-red-500 mb-4">
            <p>{error}</p>
          </div>
        )}

        {showMessage && (
          <div className="text-center text-muted-foreground px-4">
            <p className="text-xl mb-4">Showing results for: <span className="font-semibold">{keyword}</span></p>
            
            {hasResults ? (
              <SymptomWordCloud words={formattedWords} />
            ) : (
              <div className="text-center py-8">
                <p className="text-xl text-muted-foreground">No results found for "{keyword}"</p>
                <p className="text-muted-foreground">Try a different keyword</p>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
