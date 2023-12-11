// 此代码仅用于学习交流
const { WechatyBuilder } = require('wechaty');
const qrcode = require('qrcode-terminal');
const qr = require('qr-image');
const fs = require('fs');

class weChaty {
    bot = null

    constructor() {
        this.bot = WechatyBuilder.build();
        this.bot.on('scan', code => {
            qrcode.generate(code, { small: true });
            // 保存二维码为 PNG 文件
            const qrCodePath = 'qrcode.png';
            this.saveQRCodeToFile(code, qrCodePath);
        })
        // 有message消息时候触发
        this.bot.on('message', this.onMessage.bind(this));
    }

    saveQRCodeToFile(code, filePath) {
        // 保存二维码为 PNG 文件
        const qrCode = qr.image(code, { type: 'png' });
        qrCode.pipe(fs.createWriteStream(filePath));
        console.log(`QR code saved to ${filePath}`);
    }

    async onMessage(message) {
        if (message.room() && message.payload.type === 7) {
            // 获取消息的群
            const sourceRoom = message.room();
            // 获取消息的文本内容
            const content = message.text();
            const groupDirectoryPath = './group';
            const filesInGroupDirectory = fs.readFileSync(groupDirectoryPath, 'utf-8');

            // todo: 这里需要根据你的逻辑选择正确的群名
            const targetRoomTopic = filesInGroupDirectory; // 这里是一个示例，你需要根据实际情况进行修改
            const targetRoom = await this.bot.Room.find({ topic: targetRoomTopic });
            // 获取消息发送者
            const sender = message.talker();

            if (targetRoom && sourceRoom.id !== targetRoom.id) {
                // 转发消息到目标群
                targetRoom.say(`转发自群 [${await sourceRoom.topic()}]，发送者 [${sender.name()}]: ${content}`);
            } else {
                console.log(`找不到目标群或者是群 [${targetRoomTopic}] 中的消息`);
            }
        }
    }

    run() {
        this.bot.start();
    }
}

new weChaty().run();
