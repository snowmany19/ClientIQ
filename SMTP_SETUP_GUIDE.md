# 📧 SMTP Configuration Guide for CivicLogHOA

## 🎯 **Overview**

This guide will help you configure SMTP (Simple Mail Transfer Protocol) for CivicLogHOA's email notification system. Once configured, users will receive professional HTML emails for:

- 🚨 New violation notifications
- ✅ Violation resolved notifications  
- 📊 Monthly report notifications
- 🔒 Security alert notifications

## 🔧 **Step-by-Step SMTP Setup**

### **Option 1: Gmail SMTP (Recommended)**

#### **1. Enable 2-Factor Authentication**
1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Enable 2-Step Verification if not already enabled

#### **2. Generate App Password**
1. Go to Google Account settings
2. Navigate to Security → App passwords
3. Select "Mail" and "Other (Custom name)"
4. Enter "CivicLogHOA" as the name
5. Click "Generate"
6. **Copy the 16-character password** (you'll only see it once!)

#### **3. Configure Environment Variables**
Add these to your `.env` file:

```bash
# Gmail SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
FROM_EMAIL=noreply@civicloghoa.com
APP_URL=https://yourdomain.com
```

### **Option 2: Outlook/Hotmail SMTP**

#### **1. Enable App Passwords**
1. Go to Microsoft Account settings
2. Navigate to Security → Advanced security options
3. Enable "App passwords"
4. Generate a new app password

#### **2. Configure Environment Variables**
```bash
# Outlook SMTP Configuration
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@civicloghoa.com
APP_URL=https://yourdomain.com
```

### **Option 3: Yahoo SMTP**

#### **1. Generate App Password**
1. Go to Yahoo Account Security
2. Enable 2-factor authentication
3. Generate an app-specific password

#### **2. Configure Environment Variables**
```bash
# Yahoo SMTP Configuration
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@civicloghoa.com
APP_URL=https://yourdomain.com
```

### **Option 4: Custom SMTP Server**

#### **1. Get SMTP Credentials**
Contact your email provider or IT administrator for:
- SMTP server address
- Port number (usually 587 for TLS)
- Username and password

#### **2. Configure Environment Variables**
```bash
# Custom SMTP Configuration
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
FROM_EMAIL=noreply@yourdomain.com
APP_URL=https://yourdomain.com
```

## 🧪 **Testing SMTP Configuration**

### **1. Test Email Functionality**
Once configured, test the email system:

```bash
# Start the application
docker-compose up -d

# Check logs for email errors
docker-compose logs backend | grep -i email
```

### **2. Trigger Test Email**
1. Create a new violation in the dashboard
2. Check if email notifications are sent
3. Verify email delivery and formatting

### **3. Common Issues & Solutions**

| Issue | Solution |
|-------|----------|
| **Authentication failed** | Check username/password, enable 2FA, use app password |
| **Connection timeout** | Verify SMTP server and port, check firewall |
| **Emails not sending** | Check SMTP credentials, verify FROM_EMAIL |
| **Emails in spam** | Configure SPF/DKIM records, use proper FROM_EMAIL |

## 🔒 **Security Best Practices**

### **1. Use App Passwords**
- Never use your main account password
- Generate app-specific passwords
- Rotate passwords regularly

### **2. Environment Variables**
- Store SMTP credentials in `.env` files
- Never commit `.env` files to version control
- Use different credentials for dev/staging/production

### **3. Email Domain Configuration**
- Use a proper domain for FROM_EMAIL
- Configure SPF and DKIM records
- Set up DMARC policy

## 📧 **Email Templates**

The system includes 4 professional email templates:

### **1. New Violation Notification**
- 🚨 Professional alert styling
- Violation details and location
- Direct link to dashboard

### **2. Violation Resolved Notification**
- ✅ Success styling with green theme
- Resolution details and notes
- Dashboard link for review

### **3. Monthly Report Notification**
- 📊 Statistics and metrics
- Performance overview
- Full report access

### **4. Security Alert Notification**
- 🔒 Security-focused styling
- Event details and location
- Security settings link

## 🚀 **Production Deployment**

### **1. Environment Variables**
```bash
# Production SMTP Configuration
ENVIRONMENT=production
DEBUG=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=notifications@yourdomain.com
SMTP_PASSWORD=your-secure-app-password
FROM_EMAIL=noreply@yourdomain.com
APP_URL=https://yourdomain.com
```

### **2. SSL/TLS Configuration**
- Use port 587 for STARTTLS
- Ensure proper SSL certificates
- Configure reverse proxy if needed

### **3. Monitoring**
- Monitor email delivery rates
- Set up email bounce handling
- Track email engagement metrics

## 📋 **Quick Setup Checklist**

- [ ] Choose SMTP provider (Gmail recommended)
- [ ] Enable 2-factor authentication
- [ ] Generate app password
- [ ] Configure environment variables
- [ ] Test email functionality
- [ ] Verify email delivery
- [ ] Configure production settings
- [ ] Set up monitoring

## 🆘 **Troubleshooting**

### **Common Error Messages**

**"SMTP Authentication failed"**
- Check username and password
- Ensure 2FA is enabled
- Use app password, not main password

**"Connection timeout"**
- Verify SMTP server address
- Check port number (587 for TLS)
- Test network connectivity

**"Emails not sending"**
- Check SMTP credentials
- Verify FROM_EMAIL format
- Review application logs

### **Getting Help**

1. Check application logs: `docker-compose logs backend`
2. Test SMTP manually with telnet
3. Verify environment variables are loaded
4. Contact your email provider for support

## 🎉 **Success Indicators**

When SMTP is properly configured, you should see:

- ✅ Email notifications sent for new violations
- ✅ Professional HTML email formatting
- ✅ Proper sender information
- ✅ Dashboard links working correctly
- ✅ No authentication errors in logs

---

**Need help?** Check the application logs or refer to the main documentation for additional support. 