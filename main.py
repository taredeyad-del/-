const { Client, GatewayIntentBits } = require('discord.js');

const client = new Client({ 
    intents: [
        GatewayIntentBits.Guilds, 
        GatewayIntentBits.GuildMessages, 
        GatewayIntentBits.MessageContent
    ] 
});

client.once('ready', () => {
    console.log(`تم تسجيل الدخول بنجاح باسم: ${client.user.tag}`);
});

client.on('messageCreate', async message => {
    // تجاهل رسائل البوت
    if (message.author.bot) return;

    // 1. أمر الشكوى: إنشاء روم جديد باللون الأحمر مباشرة
    if (message.content.trim() === '!شكوة') {
        try {
            const channel = await message.guild.channels.create({
                name: `شكوى-🔴-${message.author.username}`,
                type: 0 // نوع الروم كتابي
            });
            
            await channel.send(`تم فتح روم الشكوى الخاص بك: ${message.author}\nيرجى كتابة تفاصيل الشكوى هنا.`);
            message.reply(`تم إنشاء روم الشكوى الخاص بك: ${channel}`);
        } catch (error) {
            console.error(error);
            message.reply('حدث خطأ أثناء إنشاء روم الشكوى، تأكد من صلاحيات البوت (إدارة القنوات).');
        }
        return;
    }

    // 2. نظام تغيير الحالة بناءً على الأوامر (يعمل داخل أي روم)
    // نستخدم مصفوفة أوامر لتسهيل الإضافة
    const statusCommands = {
        '!طلب': '🔵',
        '!تماستلامطلب': '🟢',
        '!تمارسالطلب': '🟡'
    };

    if (statusCommands[message.content]) {
        const channel = message.channel;
        const newEmoji = statusCommands[message.content];
        
        // استبدال أي إيموجي حالة سابق بالإيموجي الجديد
        const newName = channel.name.replace(/🔴|🔵|🟢|🟡/g, newEmoji);
        
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
