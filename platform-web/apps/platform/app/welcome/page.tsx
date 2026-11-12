import { redirect } from "next/navigation";
import { auth } from "../../lib/auth";

export default async function WelcomePage() {
  if (!(await auth())?.user) redirect("/sign-in");
  redirect("/");
}
