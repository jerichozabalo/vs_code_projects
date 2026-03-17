import Link from "next/link";
import fs from "fs";
import path from "path";

interface Post {
  id: string;
  title: string;
  date: string;
  content: string;
}

async function getPosts(): Promise<Post[]> {
  const filePath = path.join(process.cwd(), "data", "posts.json");
  const jsonData = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(jsonData);
}

export default async function Home() {
  const posts = await getPosts();

  return (
    <div className="min-h-screen bg-zinc-50 font-sans dark:bg-black p-4 sm:p-8 md:p-12 lg:p-20 flex justify-center">
      <main className="w-full max-w-4xl flex flex-col gap-12">
        <header className="text-center sm:text-left">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-zinc-900 dark:text-zinc-50 mb-4 tracking-tight">
            My Blog
          </h1>
          <p className="text-lg text-zinc-600 dark:text-zinc-400 max-w-2xl leading-relaxed">
            Welcome to my simple Next.js blog. Explore our latest thoughts and stories.
          </p>
        </header>

        <section className="flex flex-col gap-8">
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 border-b border-zinc-200 dark:border-zinc-800 pb-4">
            Latest Posts
          </h2>
          <div className="grid gap-6 sm:grid-cols-2">
            {posts.map((post) => (
              <article key={post.id} className="group relative bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-6 hover:shadow-xl transition-all hover:-translate-y-1">
                <Link href={`/posts/${post.id}`} className="absolute inset-0 z-10" aria-label={`Read more about ${post.title}`}>
                  <span className="sr-only">Read more</span>
                </Link>
                <div className="flex flex-col h-full gap-4">
                  <div className="flex flex-col gap-2">
                    <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                      {post.date}
                    </span>
                    <h3 className="text-xl font-bold text-zinc-900 dark:text-zinc-50 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                      {post.title}
                    </h3>
                  </div>
                  <p className="text-zinc-600 dark:text-zinc-400 line-clamp-2 text-sm leading-relaxed">
                    {post.content.replace(/<[^>]*>/g, '').substring(0, 100)}...
                  </p>
                  <div className="mt-auto pt-4 flex items-center text-sm font-semibold text-blue-600 dark:text-blue-400">
                    Read article
                    <svg className="ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
