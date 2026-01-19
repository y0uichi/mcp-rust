
export default function Home() {
  return (
    <div className="container mx-auto p-4 text-center">
      <h1 className="text-4xl font-bold mt-20">Welcome to MCP Rust</h1>
      <p className="mt-4 text-lg text-gray-400">
        The official documentation and project status website for the Rust implementation of the Multi-Component Protocol.
      </p>
      <div className="mt-10 flex justify-center gap-4">
          <a href="/docs" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Read the Docs
          </a>
          <a href="/dev" className="bg-gray-700 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded">
            See Development Progress
          </a>
      </div>
    </div>
  );
}
