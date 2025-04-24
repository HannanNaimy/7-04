import smtplib

server = smtplib.SMTP("smtp.gmail.com", 587)  
server.starttls()

server.login("hannannaimy@gmail.com", "wjuy nxha nrlf knvw") 
server.sendmail("hannannaimy@gmail.com", "1221106678@student.mmu.edu.my", "Test Email")
server.quit()
