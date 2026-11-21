import { Badge, Button, Card, CardDescription, CardTitle } from "@cre8ive/ui";

export default function AdminHomePage() {
  return (
    <main id="content" className="grid min-h-screen place-items-center px-6 py-16">
      <Card className="w-full max-w-2xl border-transparent bg-transparent p-0 text-center shadow-none">
        <Badge tone="orange">INTERNAL WORKSPACE</Badge>
        <h1 className="mt-4 text-5xl font-extrabold tracking-[-0.065em] text-charcoal sm:text-6xl">
          Hello from <span className="text-orange">Admin</span>
        </h1>
        <CardDescription className="mx-auto mt-5 max-w-lg text-base leading-7">
          Designer reviews and business operations will be managed here.
        </CardDescription>
        <div className="mt-8 flex justify-center">
          <Button size="lg">View review queue <span aria-hidden="true">↗</span></Button>
        </div>
        <CardTitle className="sr-only">Admin app scaffold</CardTitle>
      </Card>
    </main>
  );
}
