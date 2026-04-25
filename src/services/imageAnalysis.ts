import path from "node:path";

export const analyzeUploadedImage = async (filePath: string): Promise<string> => {
  const fileName = path.basename(filePath).toLowerCase();
  const signals: string[] = [];

  if (fileName.includes("front")) signals.push("front-side damage might be visible");
  if (fileName.includes("rear")) signals.push("rear-side damage might be visible");
  if (fileName.includes("plate")) signals.push("plate image may contain identifiable vehicle number");
  if (fileName.includes("wide") || fileName.includes("scene"))
    signals.push("scene context image detected");

  if (signals.length === 0) {
    return "Uploaded image received. Automated review queued; manual handler should verify visible damage zones and context.";
  }
  return `Uploaded image received. Heuristic findings: ${signals.join(", ")}.`;
};
