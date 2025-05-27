import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

const API_BASE = "http://localhost:8080/api";

async function submitLink(link: string) {
  const res = await fetch(`${API_BASE}/scrapper/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: link }),
  });
  if (!res.ok) throw new Error("Failed to submit link");
  return res.json();
}

export default function AddLinkForm() {
  const [link, setLink] = useState("");

  const mutation = useMutation({
    mutationFn: (link: string) => submitLink(link),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(link);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col items-center gap-4 mt-8 w-full max-w-md"
    >
      <input
        type="url"
        placeholder="Enter website link"
        value={link}
        onChange={(e) => setLink(e.target.value)}
        required
        className="p-2 rounded text-black w-full"
      />
      <button
        type="submit"
        className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
        disabled={mutation.isPending}
      >
        Submit
      </button>
      {mutation.isPending && <div className="mt-4">Loading...</div>}
      {mutation.isError && (
        <div className="mt-4 text-red-400">
          {(mutation.error as Error).message}
        </div>
      )}
      {mutation.isSuccess && (
        <div className="mt-4 text-green-400">
          Response: {JSON.stringify(mutation.data)}
        </div>
      )}
    </form>
  );
}
