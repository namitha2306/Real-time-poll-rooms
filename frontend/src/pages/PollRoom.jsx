import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import Toast from "../components/Toast";

const API = "http://localhost:8000";

export default function PollRoom() {
  const { id } = useParams();

  const [poll, setPoll] = useState(null);
  const [selected, setSelected] = useState(null);
  const [hasVoted, setHasVoted] = useState(false);
  const [viewers, setViewers] = useState(0);
  const [toast, setToast] = useState(null);
  const [timeLeft, setTimeLeft] = useState(null);

  // =========================
  // Fetch Poll
  // =========================
  useEffect(() => {
    fetchPoll();
  }, [id]);

  const fetchPoll = async () => {
    try {
      const res = await axios.get(`${API}/poll/${id}`);
      setPoll(res.data);

      if (res.data.expires_at) {
        startCountdown(res.data.expires_at);
      }
    } catch (err) {
      alert("Poll not found");
    }
  };
  useEffect(() => {
    const voted = localStorage.getItem(`voted_${id}`);
    if (voted) {
        setHasVoted(true);
    }
  }, [id]);

  // =========================
  // WebSocket
  // =========================
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${id}`);

    ws.onopen = () => {
      console.log("WebSocket connected ✅");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "vote_update") {
        setPoll((prev) => ({
          ...prev,
          total_votes: data.total_votes,
          options: data.options,
        }));
      }

      if (data.type === "viewer_update") {
        setViewers(data.viewers);
      }
    };

    ws.onerror = (error) => {
      console.log("WebSocket error ❌:", error);
    };

    return () => {
      ws.close();
    };
  }, [id]);

  // =========================
  // Countdown Timer
  // =========================
  const startCountdown = (expiresAt) => {
    const expiry = new Date(expiresAt + "Z").getTime();

    const interval = setInterval(() => {
      const now = new Date().getTime();
      const distance = expiry - now;

      if (distance <= 0) {
        clearInterval(interval);
        setPoll((prev) => ({
          ...prev,
          is_expired: true,
        }));
        setTimeLeft("Expired");
      } else {
        const minutes = Math.floor(distance / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        setTimeLeft(`${minutes}m ${seconds}s`);
      }
    }, 1000);
  };

  // =========================
  // Vote
  // =========================
  const vote = async () => {
    if (!selected) {
       setToast({ message: "Please select an option", type: "error" });
    return;
    }


    try {
      await axios.post(`${API}/vote/${id}`, {
        option_id: selected,
      });

      localStorage.setItem(`voted_${id}`, "true");
      setHasVoted(true);
    } catch (err) {
      setToast({
        message: err.response?.data?.detail || "Error voting",
        type: "error",
        });

    }
  };

  // =========================
  // Copy Link
  // =========================
  const copyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    setToast({ message: "Link copied to clipboard 🚀" });
  };

  if (!poll) return null;

  return (
    <div className="flex items-center justify-center min-h-screen p-6">
      <div className="bg-white/20 backdrop-blur-lg p-8 rounded-3xl shadow-2xl w-full max-w-lg border border-white/30">

        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Live Poll</h2>
          <div className="flex gap-2">
            <span className="text-sm bg-black/40 px-3 py-1 rounded-full">
              👥 {viewers}
            </span>
            <button
              onClick={copyLink}
              className="text-sm bg-white/30 px-3 py-1 rounded-full hover:bg-white/40"
            >
              🔗 Copy
            </button>
          </div>
        </div>

        {/* Expiry Badge */}
        {poll.is_expired && (
          <div className="bg-red-500/80 text-white p-2 rounded-lg mb-4 text-center">
            ⏳ This poll has expired
          </div>
        )}

        {/* Countdown */}
        {!poll.is_expired && timeLeft && (
          <div className="text-center mb-4 text-yellow-200">
            ⏱ Ends in: {timeLeft}
          </div>
        )}

        {/* Question */}
        <h1 className="text-2xl font-bold mb-6">{poll.question}</h1>

        {/* Options */}
        {poll.options.map((opt) => {
          const percentage =
            poll.total_votes > 0
              ? Math.round((opt.votes / poll.total_votes) * 100)
              : 0;

          return (
            <div key={opt.option_id} className="mb-4">
              <button
                disabled={hasVoted || poll.is_expired}
                onClick={() => setSelected(opt.option_id)}
                className={`w-full p-3 rounded-xl text-left transition ${
                  selected === opt.option_id
                    ? "bg-black text-white"
                    : "bg-white text-black"
                }`}
              >
                {opt.text}
              </button>

              {/* Results */}
              {(hasVoted || poll.total_votes > 0) && (
                <>
                  <div className="mt-2 bg-white/30 rounded-full h-3 overflow-hidden">
                    <div
                      className="bg-black h-3 transition-all duration-500"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <div className="text-sm mt-1">
                    {percentage}% ({opt.votes} votes)
                  </div>
                </>
              )}
            </div>
          );
        })}
        {toast && (
         <Toast
            message={toast.message}
            type={toast.type}
            onClose={() => setToast(null)}
            />
        )}
        {/* Vote Button */}
        {!hasVoted && !poll.is_expired && (
          <button
            onClick={vote}
            className="w-full py-3 mt-4 rounded-xl bg-black text-white font-semibold hover:bg-gray-900 transition"
          >
            Submit Vote
          </button>
        )}

        {hasVoted && (
          <div className="text-center mt-4 text-green-300 font-semibold">
            ✅ Vote submitted
          </div>
        )}
      </div>
    </div>
  );
}
