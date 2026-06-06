const { Client, GatewayIntentBits } = require('discord.js');
const client = new Client({ 
    intents: [
        GatewayIntentBits.Guilds, 
        GatewayIntentBits.GuildMessages, 
        GatewayIntentBits.MessageContent
    ] 
});

client.on('ready', () => {
    console.log(`تم تسجيل الدخول بنجاح باسم: ${client.user.tag}`);
});

client.on('messageCreate', async message => {
    if (message.author.bot) return;

    // --- 1. نظام الشكوى (يُنشئ روم جديد باللون الأحمر) ---
    if (message.content.startsWith('!شكوة')) {
        const complaintContent = message.content.replace('!شكوة', '').trim();
        if (!complaintContent) return message.reply('يرجى كتابة نص الشكوى بعد الأمر.');

        try {
            const channel = await message.guild.channels.create({
                name: `شكوى-🔴-${message.author.username}`,
                type: 0 // نوع الروم كتابي
            });
            await channel.send(`**مقدم الشكوى:** ${message.author}\n**الشكوى:** ${complaintContent}`);
            message.reply(`تم فتح روم الشكوى الخاص بك: ${channel}`);
        } catch (error) {
            console.error(error);
            message.reply('حدث خطأ أثناء إنشاء روم الشكوى، تأكد من صلاحيات البوت (MANAGE_CHANNELS).');
        }
        return;
    }

    // --- 2. نظام تغيير الحالة للأوامر (يعمل داخل الرومات) ---
    // تعريف الأوامر والإيموجي المقابل لها
    const statusCommands = {
        '!طلب': '🔵',
        '!تماستلامطلب': '🟢',
        '!تمارسالطلب': '🟡'
    };

    if (statusCommands[message.content]) {
        const channel = message.channel;
        const newEmoji = statusCommands[message.content];
        
        // استبدال الإيموجي القديم (مهما كان) بالإيموجي الجديد
        const currentName = channel.name;
        const newName = currentName.replace(/🔴|🔵|🟢|🟡/g, newEmoji);
        
        try {
            await channel.setName(newName);
            message.reply(`تم تحديث حالة الروم إلى ${newEmoji}`);
        } catch (error) {
            console.error(error);
            message.reply('عذراً، لا أملك صلاحية تغيير اسم الروم.');
        }
    }
});

// ضع الـ Token الخاص بك هنا
client.login('YOUR_BOT_TOKEN_HERE');
