export interface ChatMessage {

  role:
    | "user"
    | "assistant";

  content: string;

  provider?: string;

  sql?: string;

  rows?: any[];

  columns?: string[];

  createdAt?: string;

  loading?: boolean;

  error?: boolean;

}