import { createFileRoute } from "@tanstack/react-router";
import AddLinkForm from "../components/AddLinkForm";

export const Route = createFileRoute("/")({
  component: App,
});

function App() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <AddLinkForm />
    </div>
  );
}
