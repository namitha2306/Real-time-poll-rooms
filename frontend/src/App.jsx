import { Routes, Route } from "react-router-dom";
import CreatePoll from "./pages/CreatePoll";
import PollRoom from "./pages/PollRoom";

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-blue-500 text-white">
      <Routes>
        <Route path="/" element={<CreatePoll />} />
        <Route path="/poll/:id" element={<PollRoom />} />
      </Routes>
    </div>
  );
}

export default App;
