export type UserRole = "customer" | "designer" | "admin";

export interface User {
  id: string;
  name: string;
  email: string;
  image?: string;
  role: UserRole;
  createdAt: string;
}
