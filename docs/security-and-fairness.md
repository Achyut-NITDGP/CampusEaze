# Security and fairness
- Passwords: PBKDF2-SHA256, per-user salt. Sessions: signed JWT (8 h). Public sign-up cannot create staff or admin accounts.
- Every endpoint checks the role on the server; owners only see and decide on their own resources.
- Uploads: type allow-list (JPEG, PNG, WebP, PDF), 5 MB limit, random file names. For production, serve documents through authenticated, expiring links and keep the JWT in an HttpOnly cookie.
- Fairness: transparent limits (open bookings, hours per week), first-come waiting list, mandatory written reasons for rejections, no self-booking.
- Accountability: append-only audit log; human review for damage, disputes and eligibility.
- Accessibility: semantic landmarks, skip link, labelled forms, text (not colour alone) for status, visible focus, light/dark and reduced-motion support.
