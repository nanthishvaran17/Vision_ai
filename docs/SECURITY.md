# VisionNext AI — Security Architecture

## Security Controls

1. **Magic Byte MIME Validation**:
   Inspects header bytes (`\xff\xd8\xff` for JPEG, `\x89PNG` for PNG, `RIFF...WEBP` for WEBP). Never trusts client-declared content-types.
2. **Decompression Bomb Protection**:
   Enforces `Image.MAX_IMAGE_PIXELS = 25,000,000` to prevent memory exhaustion attacks.
3. **Password Hashing**:
   Uses Argon2id password hashing via `argon2-cffi`.
4. **JWT Security & Token Rotation**:
   Generates short-lived access JWTs (60 min) and refresh tokens with DB revocation tracking.
5. **Path Traversal Protection**:
   All uploaded images are assigned server-side SHA256/UUID filenames. Internal filesystem paths are never exposed to clients.
6. **Rate Limiting**:
   Configured via `slowapi` to prevent API abuse.
