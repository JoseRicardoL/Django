from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from correo import correoAdmin
import tempfile
import smtplib
import rrdtool
import time
import os


def gen_image(rrdpath, pngpath, fname, width, height, begdate, enddate):
    print("creando imagen")
    ldaybeg = str(begdate)
    ldayend = str(enddate)
    endd_str = time.strftime("%d/%m/%Y %H:%M:%S", (
        time.localtime(int(enddate)))).replace(':', '\:')
    begd_str = time.strftime("%d/%m/%Y %H:%M:%S", (
        time.localtime(int(begdate)))).replace(':', '\:')
    title = 'Chart for: '+fname.split('.')[0]
    pngfname = pngpath+fname.split('.')[0]+'.png'
    rrdfname = rrdpath+fname
    info = rrdtool.info(rrdfname)
    rrdtype = info['ds[inoctets].type']
    if rrdtype == 'COUNTER':
        multip = str(int(enddate) - int(begdate))
    else:
        rrdstep = info['step']
        multip = str(round((int(enddate) - int(begdate))/int(rrdstep)))
    print(rrdfname)
    rrdtool.graph(pngfname,
                  '--width', width, '--height', height,
                  '--start', str(begdate), '--end', '+2w', '--title='+title,
                  '--lower-limit', '0', '--slope-mode',
                  'COMMENT:From\:'+begd_str+'  To\:'+endd_str+'\\c',
                  'DEF:value='+rrdfname+':inoctets:AVERAGE',
                  'DEF:pred='+rrdfname+':inoctets:HWPREDICT',
                  'DEF:dev='+rrdfname+':inoctets:DEVPREDICT',
                  'DEF:fail='+rrdfname+':inoctets:FAILURES',
                  'DEF:yvalue='+rrdfname+':inoctets:AVERAGE:start='
                  ''+ldaybeg+':end='+ldayend, 'SHIFT:yvalue:86400',
                  'CDEF:upper=pred,dev,2,*,+', 'CDEF:lower=pred,dev,2,*,-',
                  'CDEF:ndev=dev,-1,*',
                  'CDEF:tot=value,'+multip+',*',
                  'CDEF:ytot=yvalue,'+multip+',*',
                  'TICK:fail#FDD017:1.0:"Failures"\\n',
                  'AREA:yvalue#C0C0C0:"Yesterday\:"',
                  'GPRINT:ytot:AVERAGE:"TotalS\:%8.0lf"',
                  'GPRINT:yvalue:MAX:"MaxS\:%8.0lf"',
                  'GPRINT:yvalue:AVERAGE:"AverageS\:%8.0lf" \\n',
                  'LINE3:value#0000ff:"Value    \:"',
                  'GPRINT:tot:AVERAGE:"Total\:%8.0lf"',
                  'GPRINT:value:MAX:"Max\:%8.0lf"',
                  'GPRINT:value:AVERAGE:"Average\:%8.0lf" \\n',
                  'LINE1:upper#ff0000:"Upper Bound "',
                  'LINE1:pred#ff00FF:"Forecast "',
                  'LINE1:ndev#000000:"Deviation "',
                  'LINE1:lower#00FF00:"Lower Bound "')


def check_aberration(rrdpath, fname, direcciones):
    print("checando aberrations")
    ab_status = 0
    rrdfilename = rrdpath+fname
    info = rrdtool.info(rrdfilename)
    rrdstep = int(info['step'])
    lastupdate = info['last_update']
    previosupdate = str((lastupdate - rrdstep*100) - 1)
    graphtmpfile = tempfile.NamedTemporaryFile()
    values = rrdtool.graph(
        graphtmpfile.name, 'DEF:f0='+rrdfilename+':inoctets:FAILURES:start='
        ''+previosupdate+':end=+1w', 'PRINT:f0:LAST:%1.0lf\n')
    flast = int(values[2][0])
    if (flast == 1):
        if direcciones[rrdfilename] == 0:
            direcciones[rrdfilename] = 1
            ab_status = 1
        else:
            ab_status = 0
    else:
        if direcciones[rrdfilename] == 1:
            direcciones[rrdfilename] = 0
            ab_status = 2
        else:
            ab_status = 0
    print("aberr: ", direcciones)
    print(ab_status)
    return ab_status, direcciones


def send_alert_attached(subject, flist, fname):
    send = correoAdmin()
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = send.mailsender
    msg['To'] = send.COMMASPACE.join(send.mailreceip)
    for f in range(len(flist)):
        png_file = flist[f]+fname[f].split('.')[0]+'.png'
        fp = open(png_file, 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        msg.attach(img)
    mserver = smtplib.SMTP(send.mailserver)
    mserver.starttls()
    mserver.login(send.username, send.password)
    mserver.sendmail(send.mailsender, send.mailreceip, msg.as_string())
    mserver.quit()
    print("enviado")


def main(paths, begdate, enddate, direcciones):
    begin_ab = []
    begin_fname = []
    end_ab = []
    end_fname = []
    width = '500'
    height = '200'
    for path in paths:
        rrdpath = path+"rrd/"
        pngpath = path+"img/"
        for fname in os.listdir(rrdpath):
            if fname.endswith(".rrd"):
                gen_image(rrdpath, pngpath, fname, width, height, begdate,
                          enddate)
    for path in paths:
        rrdpath = path+"rrd/"
        pngpath = path+"img/"
        for fname in os.listdir(rrdpath):
            if fname.endswith(".rrd"):
                print("check: ", fname)
                if rrdpath+fname not in direcciones:
                    direcciones[rrdpath+fname] = 0
                print("main: ", direcciones)
                ab_status, direcciones = check_aberration(rrdpath, fname,
                                                          direcciones)
                print(ab_status)
                if ab_status == 1:
                    begin_ab.append(pngpath)
                    begin_fname.append(fname)
                if ab_status == 2:
                    end_ab.append(pngpath)
                    end_fname.append(fname)

    if len(begin_ab) > 0:
        send_alert_attached('New aberrations detected', begin_ab, begin_fname)
        print('New aberrations detected')
        begin_ab = []
        begin_fname = []
    if len(end_ab) > 0:
        send_alert_attached('Abberations gone', end_ab, end_fname)
        print ('Abberations gone')
        end_ab = []
        end_fname = []
