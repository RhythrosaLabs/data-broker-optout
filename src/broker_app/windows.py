# windows_task.py  
#!/usr/bin/env python3
"""
Create Windows Task Scheduler XML for automated runs
"""

import os
from pathlib import Path
from datetime import datetime

def create_windows_task():
    """Create Windows Task Scheduler XML file"""
    
    script_dir = Path(__file__).parent.absolute()
    user = os.getenv('USERNAME', 'User')
    
    task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().isoformat()}</Date>
    <Author>{user}</Author>
    <Description>Automated data broker opt-out process</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{datetime.now().isoformat()}</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByMonth>
        <Months>
          <January />
          <April />
          <July />
          <October />
        </Months>
        <DaysOfMonth>
          <Day>1</Day>
        </DaysOfMonth>
      </ScheduleByMonth>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{user}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>python</Command>
      <Arguments>"{script_dir}\\main.py" --run-batch --headless</Arguments>
      <WorkingDirectory>{script_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''

    task_file = Path("OptOutBot_Task.xml")
    with open(task_file, 'w', encoding='utf-16') as f:
        f.write(task_xml)
    
    print("🪟 Windows Task Scheduler XML created!")
    print(f"✅ File: {task_file.absolute()}")
    print("\nTo import:")
    print("1. Open Task Scheduler")
    print("2. Click 'Import Task...'")
    print(f"3. Select: {task_file.absolute()}")
    print("4. Review settings and click OK")
    print("\nThe task will run every 3 months on the 1st day at the current time.")

if __name__ == "__main__":
    create_windows_task()