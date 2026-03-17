import { notFound } from "next/navigation";
import fs from "fs";
import path from "path";
import Post from "@/components/Post";

interface PostData {
  id: string;
  title: string;
  date: string;
  content: string;
}

async function getPost(id: string): Promise<PostData | null> {
  const filePath = path.join(process.cwd(), "data", "posts.json");
  const jsonData = fs.readFileSync(filePath, "utf-8");
  const posts: PostData[] = JSON.parse(jsonData);
  return posts.find((p) => p.id === id) || null;
}

export default async function PostPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const post = await getPost(id);

  if (!post) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black p-8 sm:p-20 flex justify-center">
      <div className="w-full max-w-3xl">
        <Post title={post.title} date={post.date} content={post.content} />
      </div>
    </div>
  );
}
