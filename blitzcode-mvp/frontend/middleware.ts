import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedRoutes = ["/blitz", "/contests"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isProtected = protectedRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  );

  if (!isProtected) {
    return NextResponse.next();
  }

  const isAuthenticated = request.cookies.get("blitzcode_auth")?.value === "1";

  if (isAuthenticated) {
    return NextResponse.next();
  }

  const registerUrl = request.nextUrl.clone();
  registerUrl.pathname = "/register";
  registerUrl.searchParams.set("next", pathname);

  return NextResponse.redirect(registerUrl);
}

export const config = {
  matcher: ["/blitz/:path*", "/contests/:path*"],
};
