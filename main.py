const { Client, GatewayIntentBits } = require('discord.js');

const client = new Client({ 
    intents: [
        GatewayIntentBits.Guilds, 
        GatewayIntentBits.GuildMessages, 
        GatewayIntentBits.MessageContent
    ] 
});

client.on('messageCreate', async message => {
    if (message.author.bot) return;

    // تعريف جميع الأوامر والحالات المرتبطة بها
    const statusCommands = {
        '!شكوة': '🔴',
        '!طلب': '🔵',
        '!تماستلامطلب': '🟢',
        '!تمارسالطلب': '🟡'
    };

    // التحقق إذا كانت الرسالة أحد الأوامر المذكورة
    if (statusCommands[message.content]) {
        const channel = message.channel;
        const newEmoji = statusCommands[message.content];
        
        // استبدال أي إيموجي حالة سابق موجود في الاسم بالإيموجي الجديد
        // يقوم بمسح 🔴, 🔵, 🟢, أو 🟡 ويضع الجديد
        let newName = channel.name.replace(/🔴|🔵|🟢|🟡/g, '');
        
        // إضافة الإيموجي الجديد (مع التأكد من التنسيق)
        newName = `${newName.replace(/-+$/, '')}-${newEmoji}`;

        try {
            await channel.setName(newName);
            message.reply(`تم تحديث حالة الروم إلى ${newEmoji}`);
        } catch (error) {
            console.error(error);
            message.reply('عذراً، لا أملك صلاحية تغيير اسم الروم.');
        }
    }
});

client.login('YOUR_BOT_TOKEN_HERE');
