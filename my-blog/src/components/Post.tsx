import React from "react";

interface PostProps {
  title: string;
  date: string;
  content: string;
}

const Post: React.FC<PostProps> = ({ title, date, content }) => {
  return (
    <article className="bg-white dark:bg-zinc-900 shadow-sm border border-zinc-200 dark:border-zinc-800 rounded-2xl overflow-hidden transition-shadow hover:shadow-md">
      <div className="p-6 sm:p-10 lg:p-12">
        <header className="mb-10">
          <div className="flex items-center gap-4 text-sm font-medium text-blue-600 dark:text-blue-400 mb-3">
            <span className="px-3 py-1 bg-blue-50 dark:bg-blue-900/30 rounded-full">Article</span>
            <time dateTime={date}>{date}</time>
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-zinc-900 dark:text-zinc-50 tracking-tight leading-tight">
            {title}
          </h1>
        </header>
        
        <div 
          className="prose prose-zinc dark:prose-invert prose-lg max-w-none 
            prose-headings:font-bold prose-headings:tracking-tight
            prose-a:text-blue-600 dark:prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline
            prose-strong:text-zinc-900 dark:prose-strong:text-zinc-50
            prose-img:rounded-xl"
          dangerouslySetInnerHTML={{ __html: content }} 
        />
        
        <footer className="mt-12 pt-8 border-t border-zinc-100 dark:border-zinc-800">
          <div className="flex items-center justify-between">
            <p className="text-sm text-zinc-500 dark:text-zinc-400">
              Thanks for reading!
            </p>
          </div>
        </footer>
      </div>
    </article>
  );
};

export default Post;
