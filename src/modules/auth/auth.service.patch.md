# Auth patch note
In auth.service.ts → login(), after validateUserCredentials succeeds,
add one line before generateTokens:
  await this.usersService.recordLogin(user.id)

In users.service.ts add:
  async recordLogin(id: string) {
    await this.userRepository.update(id, { lastLoginAt: new Date() })
  }
