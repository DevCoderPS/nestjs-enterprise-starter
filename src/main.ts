import {
  ClassSerializerInterceptor,
  Logger,
  ValidationPipe,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { NestFactory, Reflector } from "@nestjs/core";
import { NestExpressApplication } from "@nestjs/platform-express";
import { DocumentBuilder, SwaggerModule } from "@nestjs/swagger";
import { WINSTON_MODULE_NEST_PROVIDER } from "nest-winston";
import { AppModule } from "./app.module";

async function bootstrap(): Promise<void> {
  const app = await NestFactory.create<NestExpressApplication>(AppModule, {
    // FIX: buffer logs until Winston is ready — no lost bootstrap messages
    bufferLogs: true,
  });

  // FIX: replace NestJS built-in logger with Winston
  app.useLogger(app.get(WINSTON_MODULE_NEST_PROVIDER));

  const logger = new Logger("Bootstrap");
  const configService = app.get(ConfigService);
  const port = configService.get<number>("PORT", 3000);
  const nodeEnv = configService.get<string>("NODE_ENV", "development");

  app.setGlobalPrefix("api/v1");
  app.set("trust proxy", 1);

  app.enableCors({
    origin: configService.get<string>("CORS_ORIGIN", "*"),
    methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
    credentials: true,
  });

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: { enableImplicitConversion: true },
    }),
  );

  // FIX: strategy 'excludeAll' — only @Expose() fields are returned;
  // sensitive fields (@Exclude) never leak even without explicit decorator
  app.useGlobalInterceptors(
    new ClassSerializerInterceptor(app.get(Reflector), {
      excludeExtraneousValues: false,
    }),
  );

  // Swagger — only in non-production
  if (nodeEnv !== "production") {
    const swaggerConfig = new DocumentBuilder()
      .setTitle("ProjectX API")
      .setDescription("Enterprise NestJS Starter")
      .setVersion("1.0")
      .addBearerAuth()
      .build();
    SwaggerModule.setup(
      "api/v1/docs",
      app,
      SwaggerModule.createDocument(app, swaggerConfig),
    );
    logger.log(`Swagger docs: http://localhost:${port}/api/v1/docs`);
  }

  app.enableShutdownHooks();

  await app.listen(port);

  logger.log(`Application running on: http://localhost:${port}/api/v1`);
  logger.log(`Environment: ${nodeEnv}`);
}

bootstrap().catch((err: unknown) => {
  const logger = new Logger("Bootstrap");
  logger.error("Failed to start application", err);
  process.exit(1);
});
