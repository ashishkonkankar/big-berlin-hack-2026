import twilio from "twilio";

interface SendSmsInput {
  to: string;
  body: string;
}

const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const messagingFrom = process.env.TWILIO_FROM_NUMBER;

const client =
  accountSid && authToken
    ? twilio(accountSid, authToken)
    : null;

export const canSendSms = (): boolean => Boolean(client && messagingFrom);

export const sendSms = async ({ to, body }: SendSmsInput): Promise<void> => {
  if (!client || !messagingFrom) {
    console.log("[sms:mock]", { to, body });
    return;
  }
  await client.messages.create({
    to,
    from: messagingFrom,
    body
  });
};
