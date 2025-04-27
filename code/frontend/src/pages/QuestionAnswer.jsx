import React, { useState, useEffect } from "react";
import { Navbar } from "../components/ui/navbar";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";

export default function QuestionAnswer() {
  const [manualQuery, setManualQuery] = useState("");
  const [selectedTags, setSelectedTags] = useState([]);
  const [results, setResults] = useState([]);
  const [logs, setLogs] = useState([]);
  const [focusAreas, setFocusAreas] = useState([]);
  const [loading, setLoading] = useState(true);

  const email = localStorage.getItem("email");

  const commonSymptoms = [
    "Fever", "Cough", "Headache", "Fatigue",
    "Nausea", "Vomiting", "Shortness of breath", "Dizziness", "Sore throat"
  ];

  useEffect(() => {
    async function fetchFocusAreas() {
      try {
        // Step 1: Check localStorage
        const cached = localStorage.getItem("focusAreas");
        if (cached) {
          console.log("Loaded from localStorage");
          setFocusAreas(JSON.parse(cached));
          setLoading(false);
          return;
        }

        // Step 2: If no cache, fetch from API
        const response = await fetch("/api/focusareas");
        const data = await response.json();
        setFocusAreas(data.focusAreas || []);

        // Step 3: Save to localStorage
        localStorage.setItem("focusAreas", JSON.stringify(data.focusAreas || []));
      } catch (error) {
        console.error("Failed to fetch focus areas:", error.message);
      } finally {
        setLoading(false);
      }
    }

    fetchFocusAreas();
  }, []);


  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch(`/api/qa-search-log?email=${email}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setLogs(data);
      } catch (error) {
        console.error("Failed to fetch search logs:", error.message);
      }
    };

    if (email) {
      fetchLogs();
    }
  }, [email]);

  const handleBadgeClick = (symptom) => {
    const isSelected = selectedTags.includes(symptom);
    let updatedTags;

    if (isSelected) {
      updatedTags = selectedTags.filter((tag) => tag !== symptom);
    } else {
      updatedTags = [...selectedTags, symptom];
    }

    setSelectedTags(updatedTags);
  };

  const handleSearch = async () => {
    const finalQuery = `${manualQuery} ${selectedTags.join(" ")}`.trim();
    if (finalQuery === "") return;

    try {
      const searchParams = new URLSearchParams({
        q: finalQuery,
        email: email,
      });

      const response = await fetch(`/api/questionSearch?${searchParams.toString()}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results);
      setLogs([]);
    } catch (error) {
      console.error("Search failed:", error.message);
    }
  };

  const handleUpvote = async (questionId) => {
    try {
      const response = await fetch(`/api/questionUpvote?id=${questionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();

        const updatedResults = results.map((record) => {
          if (record.questionId === questionId) {
            return { ...record, upvotes: data.new_upvotes };
          }
          return record;
        });
        setResults(updatedResults);

      } else {
        console.error("Upvote failed");
      }
    } catch (error) {
      console.error("Error while upvoting:", error);
    }
  };

  const handleDownvote = async (questionId) => {
    try {
      const response = await fetch(`/api/questionDownvote?id=${questionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();

        const updatedResults = results.map((record) => {
          if (record.questionId === questionId) {
            return { ...record, upvotes: data.new_upvotes };
          }
          return record;
        });
        setResults(updatedResults);
      } else {
        console.error("Downvote failed");
      }
    } catch (error) {
      console.error("Error while downvoting:", error);
    }
  };

  return (
    <main className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto py-16">
        <h1 className="text-4xl font-bold mb-8 text-center text-primary">
          Question Answer
        </h1>
        <p className="mb-6 text-center">This tool allows you to search for previous question answers from the database</p>
        <div className="max-w-2xl mx-auto space-y-6">
          <Input
            type="text"
            placeholder="Search for questions"
            className="w-full"
            value={manualQuery}
            onChange={(e) => setManualQuery(e.target.value)}
          />

          <p className="text-sm text-muted-foreground italic">
            Full query:{" "}
            <span className="font-medium">{manualQuery} {selectedTags.join(" ")}</span>
          </p>

          <div className="flex flex-wrap gap-2">
            {commonSymptoms.map((symptom) => (
              <Badge
                key={symptom}
                variant="secondary"
                onClick={() => handleBadgeClick(symptom)}
                className={`cursor-pointer transition-transform ${
                  selectedTags.includes(symptom) ? "scale-95 bg-primary text-primary-foreground" : ""
                }`}
              >
                {symptom}
              </Badge>
            ))}
          </div>
          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={() => {
                setManualQuery("");
                setSelectedTags([]);
              }}
            >
              Clear Filters
            </Button>
            <Button onClick={handleSearch}>Search</Button>
          </div>
        </div> 
        {!loading && focusAreas.length > 0 && (
  <div className="overflow-x-auto mt-10">
    <table className="min-w-full bg-card border border-border rounded-lg">
      <thead>
        <tr className="bg-primary text-primary-foreground">
          <th className="py-3 px-6 text-left">Focus Area</th>
          <th className="py-3 px-6 text-left">Number of Questions</th>
          <th className="py-3 px-6 text-left">Example Question</th>
        </tr>
      </thead>
      <tbody>
        {focusAreas.map((item, index) => (
          <tr key={index} className="border-t border-border hover:bg-muted/50">
            <td className="py-3 px-6">{item.FocusArea}</td>
            <td className="py-3 px-6">{item.NumQuestions}</td>
            <td className="py-3 px-6 italic text-muted-foreground">{item.ExampleQuestion}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
)}

        {results.length === 0 && logs.length > 0 && (
          <div className="max-w-2xl mx-auto mt-10 space-y-6">
            <h2 className="text-2xl font-semibold text-primary">Your Recent Searches</h2>
            {logs.map((log, index) => (
              <div
                key={index}
                className="border border-border rounded-lg p-4 shadow-sm bg-card text-card-foreground"
              >
                <p className="text-muted-foreground italic">{log.Search_text}</p>
              </div>
            ))}
          </div>
        )}

        {results.length > 0 && (
          <div className="max-w-2xl mx-auto mt-10 space-y-6">
            <h2 className="text-2xl font-semibold text-primary">Search Results</h2>
            {results.flat().map((record, index) => (
              <div
                key={index}
                className="border border-border rounded-lg p-4 shadow-sm bg-card text-card-foreground"
              >
                {record?.question && (
                  <h3 className="text-lg font-semibold mb-2">{record.question.trim()}</h3>
                )}
                <p className="text-muted-foreground italic mb-2">
                  {record?.answer?.trim() || "No answer available."}
                </p>
                {record?.focus_area && (
                  <p className="text-sm mb-2">
                    <strong>Focus Area:</strong> {record.focus_area.trim()}
                  </p>
                )}
                <p className="text-sm mb-2">
                  <strong>Score:</strong> {record?.score?.toFixed(2) || "0.00"}
                </p>
                <div className="flex items-center justify-between mt-2">
                  <p className="text-sm text-muted-foreground">
                    Upvotes: {record.upvotes ?? 0}
                  </p>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleUpvote(record.questionId)}
                      className="text-xs text-white bg-green-600 hover:bg-green-700 px-3 py-1 rounded"
                    >
                      Upvote
                    </button>
                    <button
                      onClick={() => handleDownvote(record.questionId)}
                      className="text-xs text-white bg-red-600 hover:bg-red-700 px-3 py-1 rounded"
                    >
                      Downvote
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
