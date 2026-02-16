import { useEffect } from "react";

export default function Toast({ message, type = "success", onClose }) {

  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3000);

    return () => clearTimeout(timer);
  }, [onClose]);

  const baseStyle =
    "fixed top-6 right-6 px-6 py-4 rounded-xl shadow-2xl text-white font-medium backdrop-blur-lg border transition-all duration-500";

  const typeStyle =
    type === "error"
      ? "bg-red-500/80 border-red-300"
      : "bg-black/80 border-white/20";

  return (
    <div className={`${baseStyle} ${typeStyle}`}>
      {message}
    </div>
  );
}
