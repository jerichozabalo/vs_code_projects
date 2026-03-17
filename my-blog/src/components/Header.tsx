import Link from "next/link";
import React from "react";

const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-zinc-200 dark:bg-black dark:border-zinc-800 py-4 px-8 sm:px-20 sticky top-0 z-10">
      <div className="max-w-3xl mx-auto flex justify-between items-center">
        <Link href="/" className="text-xl font-bold text-zinc-900 dark:text-zinc-50 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
          My Blog
        </Link>
        <nav>
          <Link href="/" className="text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-50 transition-colors">
            Home
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
