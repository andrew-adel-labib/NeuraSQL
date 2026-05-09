"use client";

import Image from "next/image";

import {
  Database,
  LayoutDashboard,
  MessageSquareText,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import ProviderSelector from "./provider-selector";

interface Props {
  provider: string;
  setProvider: (provider: string) => void;
}

const menuItems = [
  {
    icon: LayoutDashboard,
    label: "AI Dashboard",
  },
  {
    icon: MessageSquareText,
    label: "Conversational Analytics",
  },
  {
    icon: Database,
    label: "SQL Intelligence",
  },
  {
    icon: ShieldCheck,
    label: "Enterprise Security",
  },
];

export default function Sidebar({
  provider,
  setProvider,
}: Props) {
  return (
    <aside
      className="
        hidden
        md:flex
        w-[320px]
        flex-col
        border-r
        border-white/10
        bg-black/20
        backdrop-blur-2xl
      "
    >

      {/* TOP BRAND */}

      <div className="border-b border-white/10 p-7">

        <div className="flex items-center gap-4">

          {/* LOGO */}

          <div
            className="
              flex
              h-14
              w-14
              items-center
              justify-center
              overflow-hidden
              rounded-lg
              border
              border-white/10
              bg-white
              p-1
            "
          >
            <Image
              src="/qbs_logo.jpg"
              alt="QBS Logo"
              width={120}
              height={60}
              className="object-contain"
              priority
            />
          </div>

          {/* TITLE */}

          <div>

            <h1
              className="
                text-2xl
                font-black
                tracking-tight
                text-white
              "
            >
              QBS AI
            </h1>

            <p
              className="
                mt-1
                text-sm
                leading-6
                text-slate-400
              "
            >
              Enterprise SQL Intelligence
            </p>

          </div>

        </div>

      </div>

      {/* MENU */}

      <div className="flex-1 overflow-y-auto p-6">

        <div className="space-y-2">

          {menuItems.map((item) => {
            const Icon = item.icon;

            return (
              <div
                key={item.label}
                className="
                  group
                  flex
                  cursor-pointer
                  items-center
                  gap-4
                  rounded-2xl
                  border
                  border-transparent
                  bg-white/[0.03]
                  px-5
                  py-4
                  transition-all
                  duration-300

                  hover:border-blue-500/20
                  hover:bg-blue-500/10
                "
              >

                <div
                  className="
                    flex
                    h-10
                    w-10
                    items-center
                    justify-center
                    rounded-xl
                    bg-slate-900/80
                    text-slate-300

                    group-hover:text-blue-300
                  "
                >
                  <Icon className="h-5 w-5" />
                </div>

                <div>

                  <div
                    className="
                      text-sm
                      font-semibold
                      text-slate-200
                    "
                  >
                    {item.label}
                  </div>

                </div>

              </div>
            );
          })}

        </div>

        {/* PROVIDER SELECTOR */}

        <div className="mt-10">

          <ProviderSelector
            provider={provider}
            setProvider={setProvider}
          />

        </div>

      </div>

      {/* FOOTER */}

      <div className="border-t border-white/10 p-6">

        <div
          className="
            flex
            items-center
            gap-3
            rounded-2xl
            border
            border-blue-500/20
            bg-blue-500/10
            px-4
            py-4
          "
        >

          <div
            className="
              flex
              h-10
              w-10
              items-center
              justify-center
              rounded-xl
              bg-blue-500/20
              text-blue-300
            "
          >
            <Sparkles className="h-5 w-5" />
          </div>

          <div>

            <div
              className="
                text-sm
                font-semibold
                text-white
              "
            >
              AI Analytics Ready
            </div>

            <div
              className="
                mt-1
                text-xs
                text-slate-400
              "
            >
              Real-time enterprise intelligence
            </div>

          </div>

        </div>

      </div>

    </aside>
  );
}