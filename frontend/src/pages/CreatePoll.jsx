import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const API = "http://localhost:8000";

export default function CreatePoll() {
  const [question, setQuestion] = useState("");
  const [options, setOptions] = useState(["", ""]);
  const [duration, setDuration] = useState(""); // expiry in minutes
  const navigate = useNavigate();

  const handleOptionChange = (index, value) => {
    const updated = [...options];
    updated[index] = value;
    setOptions(updated);
  };

  const addOption = () => {
    setOptions([...options, ""]);
  };

  const createPoll = async () => {
    if (!question.trim()) return alert("Enter a question");

    try {
      const res = await axios.post(`${API}/poll/create`, {
        question,
        options,
        duration_minutes: duration ? parseInt(duration) : null,
      });

      navigate(`/poll/${res.data.poll_id}`);
    } catch (err) {
      console.log(err.response?.data);
      alert(err.response?.data?.detail || "Error creating poll");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-6">
      <div className="bg-white/20 backdrop-blur-lg p-8 rounded-3xl shadow-2xl w-full max-w-md border border-white/30">
        
        <h1 className="text-3xl font-bold mb-6 text-center">
          🚀 Create a Live Poll
        </h1>

        {/* Question */}
        <input
          type="text"
          placeholder="Enter your question..."
          className="w-full p-3 mb-4 rounded-xl text-black"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />

        {/* Options */}
        {options.map((opt, i) => (
          <input
            key={i}
            type="text"
            placeholder={`Option ${i + 1}`}
            className="w-full p-3 mb-3 rounded-xl text-black"
            value={opt}
            onChange={(e) => handleOptionChange(i, e.target.value)}
          />
        ))}

        <button
          onClick={addOption}
          className="w-full py-2 mb-4 rounded-xl bg-white/30 hover:bg-white/40 transition"
        >
          + Add Option
        </button>

        {/* Expiry Selector */}
        <div className="mb-4">
          <label className="block mb-2 font-semibold">
            ⏳ Expiry (optional)
          </label>

          <select
            className="w-full p-3 rounded-xl text-black"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
          >
            <option value="">No expiry</option>
            <option value="1">1 minute</option>
            <option value="5">5 minutes</option>
            <option value="15">15 minutes</option>
            <option value="60">1 hour</option>
            <option value="1440">24 hours</option>
          </select>
        </div>

        {/* Create Button */}
        <button
          onClick={createPoll}
          className="w-full py-3 rounded-xl bg-black text-white font-semibold hover:bg-gray-900 transition"
        >
          Create Poll
        </button>
      </div>
    </div>
  );
}
