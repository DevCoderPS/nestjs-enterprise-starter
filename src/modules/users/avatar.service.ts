import { Injectable, Logger, BadRequestException } from "@nestjs/common";
import * as fs from "fs";
import * as path from "path";
import { v4 as uuidv4 } from "uuid";

// Store images outside the project — configurable via env
const AVATAR_DIR = process.env.AVATAR_DIR ?? "D:\\projects\\project-x-image";

const ALLOWED_MIME = ["image/jpeg", "image/png", "image/webp"];
const MAX_BYTES = 5 * 1024 * 1024; // 5 MB

@Injectable()
export class AvatarService {
  private readonly logger = new Logger(AvatarService.name);

  private ensureDir() {
    if (!fs.existsSync(AVATAR_DIR)) {
      fs.mkdirSync(AVATAR_DIR, { recursive: true });
    }
  }

  async save(
    buffer: Buffer,
    mimetype: string,
    originalName: string,
  ): Promise<string> {
    if (!ALLOWED_MIME.includes(mimetype)) {
      throw new BadRequestException(
        "Only JPEG, PNG and WebP images are allowed",
      );
    }
    if (buffer.length > MAX_BYTES) {
      throw new BadRequestException("Image must be smaller than 5 MB");
    }

    this.ensureDir();

    const ext = path.extname(originalName) || ".jpg";
    const filename = `${uuidv4()}${ext}`;
    const fullPath = path.join(AVATAR_DIR, filename);

    fs.writeFileSync(fullPath, buffer);
    this.logger.log(`Avatar saved: ${fullPath}`);

    // Return the relative path stored in the DB
    return `avatars/${filename}`;
  }

  delete(relativePath: string | null) {
    if (!relativePath) return;
    try {
      const fullPath = path.join(AVATAR_DIR, path.basename(relativePath));
      if (fs.existsSync(fullPath)) {
        fs.unlinkSync(fullPath);
        this.logger.log(`Avatar deleted: ${fullPath}`);
      }
    } catch (err) {
      this.logger.warn(`Could not delete avatar: ${err}`);
    }
  }
}
