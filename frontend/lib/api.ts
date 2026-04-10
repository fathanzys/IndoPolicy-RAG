import axios from "axios";

export const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export async function askQuestion(question: string) {
  const res = await api.post("/api/ask", { question });
  return res.data.answer as string;
}
