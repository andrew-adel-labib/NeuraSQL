"use client";

import Image from "next/image";
import { useState } from "react";

import Sidebar from "@/components/sidebar";
import ChatWindow from "@/components/chat-window";

export default function Home() {
  const [provider, setProvider] = useState("claude");

  return (
    <main
      className="
        flex
        h-screen
        overflow-hidden
        bg-gradient-to-br
        from-[#020817]
        via-[#071329]
        to-[#0f172a]
      "
    >
      {/* SIDEBAR */}

      <Sidebar
        provider={provider}
        setProvider={setProvider}
      />

      {/* MAIN CONTENT */}

      <section className="flex flex-1 flex-col overflow-hidden">

        {/* HEADER */}

        <div className="border-b border-white/10 px-10 py-8">

          <div
            className="
              glass
              gradient-border
              rounded-3xl
              p-8
              shadow-2xl
            "
          >

            <div className="flex items-center gap-5">

              {/* LOGO */}

              <div
                className="
                  flex
                  h-16
                  w-28
                  items-center
                  justify-center
                  overflow-hidden
                  rounded-xl
                  border
                  border-white/10
                  bg-white
                  p-2
                "
              >
                <Image
                  src="/qbs_logo.jpg"
                  alt="QBS Logo"
                  width={140}
                  height={70}
                  className="object-contain"
                  priority
                />
              </div>

              {/* TITLE */}

              <div>

                <h1
                  className="
                    text-4xl
                    font-black
                    tracking-tight
                    text-white
                  "
                >
                  QBS AI Analytics
                </h1>

                <p
                  className="
                    mt-2
                    text-base
                    leading-7
                    text-slate-400
                  "
                >
                  Enterprise conversational AI analytics
                  powered by SQL intelligence
                </p>

              </div>

            </div>

          </div>

        </div>

        {/* CHAT WINDOW */}

        <div className="flex-1 overflow-hidden">

          <ChatWindow provider={provider} />

        </div>

      </section>

    </main>
  );
}