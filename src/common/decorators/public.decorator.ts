import { SetMetadata } from '@nestjs/common';

export const IS_PUBLIC_KEY = 'isPublic';

/**
 * Mark a route as public — bypasses JwtAuthGuard globally.
 * Import from here; do NOT redefine elsewhere.
 */
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);
