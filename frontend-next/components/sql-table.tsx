"use client";

import {
  Database,
  Table2,
} from "lucide-react";

interface Props {
  rows: any[];
}

export default function SqlTable({
  rows,
}: Props) {

  if (!rows || rows.length === 0) {
    return null;
  }

  const columns = Object.keys(rows[0]);

  return (
    <div className="mt-6">

      {/* HEADER */}

      <div
        className="
          mb-4
          flex
          items-center
          justify-between
        "
      >

        <div className="flex items-center gap-3">

          <div
            className="
              flex
              h-10
              w-10
              items-center
              justify-center
              rounded-xl
              border
              border-blue-500/20
              bg-blue-500/10
              text-blue-300
            "
          >
            <Database className="h-5 w-5" />
          </div>

          <div>

            <h3
              className="
                text-sm
                font-semibold
                text-white
              "
            >
              SQL Query Results
            </h3>

            <p
              className="
                text-xs
                text-slate-400
              "
            >
              {rows.length} rows returned from database
            </p>

          </div>

        </div>

        <div
          className="
            flex
            items-center
            gap-2
            rounded-xl
            border
            border-white/10
            bg-white/[0.03]
            px-3
            py-2
            text-xs
            text-slate-300
          "
        >
          <Table2 className="h-4 w-4" />
          Live Data
        </div>

      </div>

      {/* TABLE */}

      <div
        className="
          overflow-hidden
          rounded-3xl
          border
          border-white/10
          bg-slate-950/70
          shadow-2xl
          backdrop-blur-xl
        "
      >

        <div className="overflow-x-auto">

          <table className="w-full border-collapse">

            {/* HEADER */}

            <thead
              className="
                border-b
                border-white/10
                bg-white/[0.03]
              "
            >

              <tr>

                {columns.map((column) => (

                  <th
                    key={column}
                    className="
                      whitespace-nowrap
                      px-6
                      py-4
                      text-left
                      text-xs
                      font-bold
                      uppercase
                      tracking-wider
                      text-slate-300
                    "
                  >
                    {column}
                  </th>

                ))}

              </tr>

            </thead>

            {/* BODY */}

            <tbody>

              {rows.map((row, rowIndex) => (

                <tr
                  key={rowIndex}
                  className="
                    border-b
                    border-white/5
                    transition-colors
                    duration-200

                    hover:bg-blue-500/[0.04]
                  "
                >

                  {columns.map((column) => (

                    <td
                      key={column}
                      className="
                        whitespace-nowrap
                        px-6
                        py-4
                        text-sm
                        text-slate-200
                      "
                    >

                      <div
                        className="
                          max-w-[300px]
                          truncate
                        "
                      >
                        {row[column] !== null &&
                        row[column] !== undefined
                          ? String(row[column])
                          : "-"}
                      </div>

                    </td>

                  ))}

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      </div>

    </div>
  );
}