<template>
   <el-container class="app-container">
     <el-header class="app-header">
       <div class="header-inner">
         <div class="logo-wrapper">
           <img src="./assets/gesilogo.png" alt="Logo" class="logo" />
         </div>
         <div class="brand-block">
           <h1>线缆点位测试表转换软件</h1>
           <p class="eyebrow">MVP 工作流</p>
         </div>
       </div>
     </el-header>
     <el-main class="app-main">
       <div class="page-container">
         <router-view />
       </div>
     </el-main>
     <el-footer class="app-footer">
       <div class="footer-inner">
         <span class="footer-text">研发单位：卫星数字化技术重点实验室</span>
       </div>
     </el-footer>
   </el-container>
 </template>

 <style scoped>
 /* 全局容器 */
 .app-container {
   min-height: 100vh;
   background: #f7f8fa;
   display: flex;
   flex-direction: column;
 }

 .app-main {
   flex: 1;
 }

 /* 头部 */
 .app-header {
   height: auto;
   padding: 12px 24px 10px;
   background: #ffffff;
   border-bottom: 1px solid #e5e7eb;
 }

 .header-inner {
   display: flex;
   align-items: center;
   gap: 20px;
   width: 100%;
   max-width: 1200px;
   margin: 0 auto;
 }

 .logo-wrapper {
   flex-shrink: 0;
 }

 .logo {
   width: 70px;
   height: 70px;
   object-fit: contain;
   transform: translateY(10px);
 }

 /* 标题文字区域 */
 .brand-block {
   display: flex;
   flex-direction: column;
   gap: 4px;
 }

 .app-header h1 {
   margin: 0;
   font-size: 26px;
   line-height: 1.25;
   font-weight: 600;
   color: #1f2937;
 }

 .eyebrow {
   margin: 4px 0 0;
   font-size: 13px;
   font-weight: 500;
   color: #6b7280;
   letter-spacing: 0.06em;
 }

 /* 主体内容 */
 .app-main {
   display: flex;
   justify-content: center;
   padding: 16px 24px 20px;
 }

 .page-container {
   width: 100%;
   max-width: 1200px;
 }

 /* 底部 */
 .app-footer {
   padding: 20px 24px;
   background: #ffffff;
   border-top: 1px solid #e5e7eb;
 }

 .footer-inner {
   display: flex;
   justify-content: center;
 }

 .footer-text {
   font-size: 12px;
   color: #9ca3af;
 }

 /* 移动端自适应 */
 @media (max-width: 768px) {
   .app-header {
     padding: 12px 16px 10px;
   }

   .logo {
     width: 56px;
     height: 56px;
   }

   .header-inner {
     gap: 16px;
   }

   .app-header h1 {
     font-size: 22px;
   }

   .app-main {
     padding: 20px 12px 32px;
   }
 }
 </style>